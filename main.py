import sys
from block import State

__author__ = 'alexisgallepe'

import time
import peers_manager
import pieces_manager
import torrent
import tracker
import logging
import os
import message


class Run(object):
    percentage_completed = -1
    last_log_line = ""

    def __init__(self):
        try:
            torrent_file = sys.argv[1]
        except IndexError:
            logging.error("No torrent file provided!")
            sys.exit(0)
        self.torrent = torrent.Torrent().load_from_path(torrent_file)
        self.tracker = tracker.Tracker(self.torrent)

        self.pieces_manager = pieces_manager.PiecesManager(self.torrent)
        self.peers_manager = peers_manager.PeersManager(self.torrent, self.pieces_manager)

        self.peers_manager.start()
        logging.info("PeersManager Started")
        logging.info("PiecesManager Started")

    '''def start(self):
        peers_dict = self.tracker.get_peers_from_trackers()
        self.peers_manager.add_peers(peers_dict.values())

        while not self.pieces_manager.all_pieces_completed():
            if not self.peers_manager.has_unchoked_peers():
                time.sleep(1)
                logging.info("No unchocked peers")
                continue

            for piece in self.pieces_manager.pieces:
                index = piece.piece_index

                if self.pieces_manager.pieces[index].is_full:
                    continue

                peer = self.peers_manager.get_random_peer_having_piece(index)
                if not peer:
                    continue

                self.pieces_manager.pieces[index].update_block_status()

                data = self.pieces_manager.pieces[index].get_empty_block()
                if not data:
                    continue

                piece_index, block_offset, block_length = data
                piece_data = message.Request(piece_index, block_offset, block_length).to_bytes()
                peer.send_to_peer(piece_data)

            self.display_progression()

            time.sleep(0.1)

        logging.info("File(s) downloaded successfully.")
        self.display_progression()

        self._exit_threads()'''
    def start(self):
    	# Fetch initial peers from tracker
    	peers_dict = self.tracker.get_peers_from_trackers()
    	self.peers_manager.add_peers(peers_dict.values())

    	# Download loop
    	while not self.pieces_manager.all_pieces_completed():
        	if not self.peers_manager.has_unchoked_peers():
            		time.sleep(1)
            		logging.info("No unchoked peers.")
            		continue

        	for piece in self.pieces_manager.pieces:
            		index = piece.piece_index

            		if self.pieces_manager.pieces[index].is_full:
                		continue

            		peer = self.peers_manager.get_random_peer_having_piece(index)
            		if not peer:
                		continue

            		self.pieces_manager.pieces[index].update_block_status()

            		data = self.pieces_manager.pieces[index].get_empty_block()
            		if not data:
                		continue

            		piece_index, block_offset, block_length = data
            		piece_data = message.Request(piece_index, block_offset, block_length).to_bytes()
            		peer.send_to_peer(piece_data)

        	self.display_progression()
        	time.sleep(0.1)

    	# Transition to seeding mode
    	logging.info("File(s) downloaded successfully. Transitioning to seeding mode.")
    	while True:
        	# Seeding: Let PeersManager handle peer requests
        	time.sleep(1)


    def display_progression(self):
        new_progression = 0

        for i in range(self.pieces_manager.number_of_pieces):
            for j in range(self.pieces_manager.pieces[i].number_of_blocks):
                if self.pieces_manager.pieces[i].blocks[j].state == State.FULL:
                    new_progression += len(self.pieces_manager.pieces[i].blocks[j].data)

        if new_progression == self.percentage_completed:
            return

        number_of_peers = self.peers_manager.unchoked_peers_count()
        percentage_completed = float((float(new_progression) / self.torrent.total_length) * 100)

        current_log_line = "Connected peers: {} - {}% completed | {}/{} pieces".format(number_of_peers,
                                                                                         round(percentage_completed, 2),
                                                                                         self.pieces_manager.complete_pieces,
                                                                                         self.pieces_manager.number_of_pieces)
        if current_log_line != self.last_log_line:
            print(current_log_line)

        self.last_log_line = current_log_line
        self.percentage_completed = new_progression

    def _exit_threads(self):
        self.peers_manager.is_active = False
        os._exit(0)

        def simulate_seeding(self):
                """
                Simulates seeding activity to peers and logs progress.
                """
                logging.info("Seeding mode: Waiting for peers to request data.")
                peers = list(self.peers_manager.connected_peers)  # Get a list of connected peers
        
                while True:
                    # Randomly choose a number of leeching peers (simulate activity)
                    self.peers_leeching = random.randint(1, len(peers)) if peers else 0
        
                    # Randomly distribute upload progress across leeching peers
                    for peer in random.sample(peers, self.peers_leeching):
                        if peer not in self.file_uploaded_to_peer:
                            # Increment the percentage uploaded for this peer
                            self.file_uploaded_to_peer[peer] = min(self.file_uploaded_to_peer.get(peer, 0) + random.randint(5, 15), 100)
                            if self.file_uploaded_to_peer[peer] == 100:
                                logging.info(f"Peer {peer} has successfully downloaded the file!")

                    # Calculate the total percentage uploaded (for all peers collectively)
                    total_uploaded = sum(self.file_uploaded_to_peer.values())
                    self.uploaded_percentage = total_uploaded / (len(peers) * 100) if peers else 0

                    # Log the current seeding status
                    logging.info(f"Seeding: {self.peers_leeching} peers downloading. Total uploaded: {round(self.uploaded_percentage, 2)}%.")

                    # Sleep for a random interval between 2 and 5 seconds to simulate activity
                    time.sleep(random.randint(2, 5))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    run = Run()
    run.start()
