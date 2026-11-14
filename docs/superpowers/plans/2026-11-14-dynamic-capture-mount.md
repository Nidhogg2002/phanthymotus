# Dynamic capture mount integration

Preserve user-validated estimated matrices and their provenance. Do not change
running cards, deploy, alter capture stamps, freeze a dynamic mount, or widen
any freshness, interpolation, clock or TF threshold.

1. Driver explicitly declares the host realtime reference (kernel boot identity)
   of normalized chassis timestamps and Orbbec global capture headers. This is
   clock-domain identity, not measured timestamp accuracy; retain unknown camera
   mapping uncertainty. No matching by numerical proximity or robot names.
2. Core forwards connected metric cloud camera_info only. SLAM runtime discovery
   may select the declared capture-time body_mount when cloud and pose frames
   differ and both producers declare the same host clock reference. Preserve the
   existing full input-contract path, including its stricter clock proofs.
3. Reuse CaptureMounts identity/clock/500 ms freshness checks and exact nanosecond
   joins. Bound waiting clouds; never use latest/nearest/held TF. Pass each matrix
   into the existing dynamic SlamStream/native TF path. Retire broken identities;
   preserve raw cloud bytes, capture stamp and calibration provenance.
4. Tests first: dynamic matrices across captures, both arrival orders, missing/
   stale/invalid/changed mount, missing or mismatched clock reference, and source
   port routing. Test actual ROS gateway integration and unchanged static paths.
5. Run relevant Driver/Core/Perception suites, full Perception, independent review,
   then normal pushes to PR519/PR371. Field activation needs user deployment of
   Core and Perception plus the Driver opt-in estimated-certificate configuration.

This route does not certify physical mounting accuracy or a new camera clock
error bound. It retains the runtime route's declared (not strictly verified)
clock provenance; it cannot replace or weaken an explicit full SLAM contract.
