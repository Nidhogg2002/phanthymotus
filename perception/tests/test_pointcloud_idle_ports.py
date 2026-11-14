"""An idle canvas card retains ports without borrowing another instance's topics."""
import pytest
from test_pointcloud_plugin import _plugin


@pytest.mark.parametrize('inputs', [{}, {'input_topic': ''}, {'input_topic': '/depth'},
                                    {'input_topics': ['/depth']}])
@pytest.mark.parametrize('metric', [False, True])
def test_idle_ports_resolve_only_from_this_cards_input(inputs, metric):
    plugin, executor = _plugin()
    plugin.dispatch('pointcloud', {'action': 'config', 'instance_id': 'idle', 'metric_cloud': metric})
    info = plugin.dispatch('pointcloud', {'action': 'info', 'instance_id': 'idle', **inputs})
    expected = [{'format': 'sensor/pointcloud'}, {'format': 'data/json'}]
    if metric:
        expected.append({'format': 'sensor/pointcloud2'})
    if inputs.get('input_topic') or inputs.get('input_topics'):
        for port, suffix in zip(expected, ('pointcloud', 'pointcloud_summary', 'pointcloud_metric')):
            port['topic'] = '/depth/' + suffix
    assert info['topic_out'] == expected
    assert info['state'] == 'idle' and info['instances'] == {}
    assert not executor.nodes and not plugin._nodes
    assert 'camera_info' not in info and 'input_metadata' not in info


def test_idle_card_never_inherits_running_cards_ports_or_calibration():
    plugin, _ = _plugin()
    try:
        plugin.dispatch('pointcloud', {'action': 'start', 'instance_id': 'other', 'input_topic': '/other'})
        info = plugin.dispatch('pointcloud', {'action': 'info', 'instance_id': 'idle', 'input_topic': '/depth'})
        assert info['state'] == 'idle' and info['instances'] == {}
        assert info['topic_out'] == [{'topic': '/depth/pointcloud', 'format': 'sensor/pointcloud'},
                                     {'topic': '/depth/pointcloud_summary', 'format': 'data/json'}]
        assert not info['topic_in']
        assert 'camera_info' not in info and 'input_metadata' not in info
        running = plugin.dispatch('pointcloud', {'action': 'info', 'instance_id': 'other'})
        assert running['state'] == 'running'
        assert running['topic_out'][0]['topic'] == '/other/pointcloud'
    finally:
        plugin.shutdown()


@pytest.mark.parametrize('inputs', [{'input_topics': ['/a', '/b']},
                                    {'input_topic': '/a', 'input_topics': ['/b']},
                                    {'input_topic': '/rgb', 'camera_info': {'/rgb': {'format': 'image/jpeg'}}}])
def test_idle_invalid_input_does_not_advertise_guessed_topics(inputs):
    plugin, executor = _plugin()
    info = plugin.dispatch('pointcloud', {'action': 'info', 'instance_id': 'idle', **inputs})
    assert info['state'] == 'error'
    assert all(not p.get('topic') for p in info['topic_out'])
    assert not executor.nodes


def test_stop_and_rewire_rederive_idle_ports_and_preserve_metric_config():
    plugin, _ = _plugin({'metric_cloud': True})
    plugin.dispatch('pointcloud', {'action': 'config', 'instance_id': 'card', 'metric_cloud': False})
    try:
        plugin.dispatch('pointcloud', {'action': 'start', 'instance_id': 'card', 'input_topic': '/old'})
        plugin.dispatch('pointcloud', {'action': 'stop', 'instance_id': 'card'})
        info = plugin.dispatch('pointcloud', {'action': 'info', 'instance_id': 'card', 'input_topic': '/new'})
        assert [p['topic'] for p in info['topic_out']] == ['/new/pointcloud', '/new/pointcloud_summary']
        empty = plugin.dispatch('pointcloud', {'action': 'info', 'instance_id': 'card', 'input_topic': ''})
        assert len(empty['topic_out']) == 2 and all(not p.get('topic') for p in empty['topic_out'])
    finally:
        plugin.shutdown()
