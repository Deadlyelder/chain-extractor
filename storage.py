import traceback, time, os
from urllib.parse import quote_plus

# Using MongoDB, can be changed to traditional RDS later

from pymongo import MongoClient, ASCENDING 
from pymongo.errors import OperationFailure, DuplicateKeyError 

from common import GENESIS_HASH # Later to be parsed from config

class DBIntegrityException(Exception):
    """custom db integrity exception"""
    pass

class Mongo:
    """
    Class responsible for handling the mango db
    """

    def __init__(self, logger):
        self.logger = logger
        self.database = self.establish_connection()
        self.collection = self.database.blocks
        self.saved_blocks_hashes = set()
        self.add_readonly_user()
        self.create_indexes()

    def establish_connection(self):
        """Connection Establisher"""

        while True:
            try:
                mongo_container = 'localhost'
                self.logger.info('connecting to mongo at: {}'.format(
                    mongo_container
                ))
                username = quote_plus(os.environ['MONGODB_ADMIN_USER'])
                password = quote_plus(os.environ['MONGODB_ADMIN_PASS'])
                connection = MongoClient('mongodb://{}:{}@{}'.format(
                    username, password, mongo_container
                ))
                database = connection[os.environ['CRYPTO']]
                return database
            except OperationFailure as exception:
                self.logger.error('Error {}, retrying in 1s'.format(exception))
                time.sleep(1)

    def add_readonly_user(self):
        """add_readonly_user"""
        try:
            self.database.command(
                "createUser",
                os.environ['MONGODB_READONLY_USER'],
                pwd=os.environ['MONGODB_READONLY_PASS'],
                roles=[{'role': 'read', 'db': os.environ['CRYPTO']}]
            )
        except DuplicateKeyError:
            pass

    @property
    def blocks_collection(self):
        """Collect Blocks"""
        return self.collection

    @property
    def hash_and_height_of_last_saved_block(self):
        """The hash and height of the last block reference"""
        last_block = self.collection.find().sort([('height', -1)]).limit(1)
        if last_block.count() != 0:
            return last_block[0]['hash'], last_block[0]['height']
        return GENESIS_HASH, -1

    @property
    def hash_of_last_saved_block(self):
        return self.hash_and_height_of_last_saved_block[0]

    def save_block(self, block):
        """Save the block info"""
        if block['hash'] in self.saved_blocks_hashes:
            raise DBIntegrityException(
                'Block Hash not unique for block {}'.format(
                    block['hash']
                )
            )
        self.saved_blocks_hashes.add(block['hash'])
        self.collection.insert_one(block)

    def check_hash_uniqueness(self, block_hash):
        """Verify that we dont have duplicate blocks"""
        return block_hash not in self.saved_blocks_hashes

    def create_indexes(self):
        """Generate the indexes"""
        self.logger.info('Creating height db index')
        self.collection.create_index([('height', ASCENDING)])
        self.logger.info('Creating timestamp db index')
        self.collection.create_index([('timestamp', ASCENDING)])
        self.logger.info('Creating tx hash db index')
        self.collection.create_index([('tx.txid', ASCENDING)])

    def get_tx_out_addr(self, tx_hash, out_index):
        """Generate the transaction and address"""
        try:
            result = None
            result = self.collection.find_one(
                {'tx.txid': tx_hash},
                {'tx.vout.$': 1}
            )
            return result['tx'][0]['vout'][out_index]['scriptPubKey']['addresses']
        except Exception as e:
            self.logger.error(f'{traceback.format_exc()} '
                              f'for txid:index {tx_hash}:{out_index} '
                              f'query result {result}')
            return []