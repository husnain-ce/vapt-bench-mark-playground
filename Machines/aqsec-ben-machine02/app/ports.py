from collections import defaultdict


def choose_external_ports(specs, occupied, start_fallback=2222):
    """
    Preserve the host's existing listening ports.

    Rules:
    1. If a guest port number is completely free for all required protocols,
       keep the same external port.
    2. If the host already uses that port for any required protocol, do not
       disturb the host service.
    3. Find one new external port number that is free for every protocol used
       by that guest port.
    4. TCP/UDP pairs for the same guest port stay on the same external number.

    Example:
      host uses tcp/22 and tcp+udp/53

      guest 21/tcp -> 21
      guest 22/tcp -> 2222
      guest 53/tcp -> 2223
      guest 53/udp -> 2223
      guest 80/tcp -> 80
    """

    # Normalize occupied set.
    occupied = {(str(proto).lower(), int(port)) for proto, port in occupied}

    # Group requested protocols by guest port.
    grouped = defaultdict(list)
    for item in specs:
        guest = int(item["guest"])
        proto = item.get("protocol", "tcp").lower()
        grouped[guest].append(proto)

    mappings_by_guest = {}
    reserved = set(occupied)

    # Track external port numbers already allocated to another guest service.
    # This keeps mappings easy to understand and avoids reusing 2222 for
    # unrelated services even when protocols differ.
    allocated_external_numbers = set()

    next_fallback = start_fallback

    for guest in sorted(grouped):
        protocols = grouped[guest]

        original_is_free = all(
            (proto, guest) not in reserved
            for proto in protocols
        )

        if original_is_free and guest not in allocated_external_numbers:
            external = guest
        else:
            candidate = max(next_fallback, 1024)

            while True:
                protocol_conflict = any(
                    (proto, candidate) in reserved
                    for proto in protocols
                )

                numeric_conflict = candidate in allocated_external_numbers

                if not protocol_conflict and not numeric_conflict:
                    external = candidate
                    break

                candidate += 1

            next_fallback = external + 1

        allocated_external_numbers.add(external)

        for proto in protocols:
            reserved.add((proto, external))

        mappings_by_guest[guest] = external

    result = []

    # Preserve original config ordering in displayed output.
    for item in specs:
        guest = int(item["guest"])
        proto = item.get("protocol", "tcp").lower()

        result.append({
            "guest": guest,
            "external": mappings_by_guest[guest],
            "protocol": proto,
        })

    return result
