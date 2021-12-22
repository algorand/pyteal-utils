"""Module containing helper functions for testing PyTeal Utils."""

from algosdk.v2client import algod, indexer


# CLIENTS
###############################################################################
def _algod_client():
    """Instantiate and return Algod client object."""
    algod_address = "http://localhost:4001"
    algod_token = "a" * 64
    return algod.AlgodClient(algod_token, algod_address)


def _indexer_client():
    """Instantiate and return Indexer client object."""
    indexer_address = "http://localhost:8980"
    indexer_token = "a" * 64
    return indexer.IndexerClient(indexer_token, indexer_address)
