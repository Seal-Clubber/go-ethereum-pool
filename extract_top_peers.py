from collections import defaultdict

GETH_LOGFILE = 'geth-log.txt'


def extract_parameter(source_str, before_str, after_str):
    start_pos = source_str.find(before_str) + len(before_str)
    return source_str[start_pos:source_str.find(after_str, start_pos)]


def extract_top_peers_from_logs():
    logs = open(GETH_LOGFILE, 'r').readlines()
    # count imports
    block_imports = [line for line in logs if 'Importing propagated block' in line]
    peer_id_to_block_count = defaultdict(int)
    for block_import_line in block_imports:
        peer_id = extract_parameter(block_import_line, 'peer=', ' ')
        peer_id_to_block_count[peer_id] += 1
    # convert peer IDs to enodes
    peer_id_to_enode = defaultdict(str)
    peer_logs = [line for line in logs if 'Peer:' in line]
    for peer_log_line in peer_logs:
        peer_id = extract_parameter(peer_log_line, 'id=', ' ')
        enode = extract_parameter(peer_log_line, 'enode=', ' ')
        # potentially problematic if there are overlaps, but for simplicity just take the latest chronologically
        peer_id_to_enode[peer_id] = enode
    # merge top enodes together
    peer_id_and_block_counts = list(peer_id_to_block_count.items())
    peer_id_and_block_counts.sort(key=lambda x: x[1], reverse=True)
    enodes = []
    for peer_id, block_count in peer_id_and_block_counts:
        if peer_id_to_enode[peer_id]:
            enodes.append(peer_id_to_enode[peer_id])
    return enodes[:50]


if __name__ == '__main__':
    top_peers_from_logs = extract_top_peers_from_logs()
    nodes_data = (
            '[\n' +
            ',\n'.join(
                '    "' + enode + '"'
                for enode in top_peers_from_logs
            )
            + '\n]'
    )
    with open('trusted_nodes.json', 'w') as nodes_file:
        nodes_file.write(nodes_data)
