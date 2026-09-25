from collections import defaultdict


def choose_external_ports(specs, occupied, start_fallback=2222):
    """Preserve Ubuntu host ports; remap only VM conflicts."""
    occupied = {(str(proto).lower(), int(port)) for proto, port in occupied}

    grouped = defaultdict(list)
    for item in specs:
        guest = int(item["guest"])
        proto = item.get("protocol", "tcp").lower()
        grouped[guest].append(proto)

    mappings_by_guest = {}
    reserved = set(occupied)
    allocated_external_numbers = set()
    next_fallback = start_fallback

    for guest in sorted(grouped):
        protocols = grouped[guest]
        original_is_free = all((proto, guest) not in reserved for proto in protocols)
        if original_is_free and guest not in allocated_external_numbers:
            external = guest
        else:
            candidate = max(next_fallback, 1024)
            while True:
                protocol_conflict = any((proto, candidate) in reserved for proto in protocols)
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
    for item in specs:
        guest = int(item["guest"])
        proto = item.get("protocol", "tcp").lower()
        result.append({"guest": guest, "external": mappings_by_guest[guest], "protocol": proto})
    return result
