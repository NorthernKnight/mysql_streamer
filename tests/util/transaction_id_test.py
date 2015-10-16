# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from replication_handler.util.transaction_id import TransactionId


class TestTransactionId(object):

    @pytest.fixture(params=[
        [str('cluster1'), 'bin_log1', 10],
        ['cluster1', str('bin_log1'), 10],
        ['cluster1', 'bin_log1', '10'],
    ])
    def invalid_params(self, request):
        return request.param

    def test_transaction_id_rejects_invalid_params(self, invalid_params):
        with pytest.raises(TypeError):
            TransactionId(*invalid_params)

    @pytest.fixture(params=[
        ['cluster1', 'bin_log1', 10],
    ])
    def valid_params(self, request):
        return request.param

    @pytest.fixture
    def transaction_id(self, valid_params):
        return TransactionId(*valid_params)

    @pytest.fixture(params=[
        {'cluster_name': 'cluster1', 'log_file': 'bin_log1', 'log_pos': 10},
    ])
    def expected_to_dict(self, request):
        return request.param

    @pytest.fixture(params=[
        'cluster1:bin_log1:10',
    ])
    def expected_str_repr(self, request):
        return request.param

    def test_transaction_id_payload(self, transaction_id, expected_to_dict):
        assert transaction_id.payload == expected_to_dict

    def test_transaction_id_str_repr(self, transaction_id, expected_str_repr):
        assert str(transaction_id) == expected_str_repr

    def test_equality(self, valid_params):
        transaction_id_1 = TransactionId(*valid_params)
        transaction_id_2 = TransactionId(*valid_params)

        assert transaction_id_1 == transaction_id_1
        assert transaction_id_1 == transaction_id_2
        assert transaction_id_2 == transaction_id_2

    def test_inequality(self, valid_params):
        transaction_id_params = list(valid_params)
        transaction_id_1 = TransactionId(*transaction_id_params)
        transaction_id_params[0] = 'different_cluster'
        transaction_id_2 = TransactionId(*transaction_id_params)

        assert transaction_id_1 != transaction_id_2

    def test_hash(self, valid_params):
        transaction_id_1 = TransactionId(*valid_params)
        transaction_id_2 = TransactionId(*valid_params)
        test_dict = {transaction_id_1: 'message1'}
        assert transaction_id_2 in test_dict
        assert test_dict[transaction_id_2] == 'message1'
