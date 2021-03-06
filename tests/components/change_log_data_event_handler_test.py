# -*- coding: utf-8 -*-
# Copyright 2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
import pytest

from replication_handler.components.change_log_data_event_handler import ChangeLogDataEventHandler


class TestChangeLogDataEventHandler(object):

    @pytest.fixture
    def event_handler(self, mock_db_connections):
        return ChangeLogDataEventHandler(
            db_connections=mock_db_connections,
            producer=mock.MagicMock(),
            schema_wrapper=mock.MagicMock(),
            stats_counter=mock.MagicMock(),
            register_dry_run=False,
            gtid_enabled=False
        )

    def test_get_schema_id(self, mock_db_connections):
        schema_wrapper = mock.MagicMock()
        schematizer_client = schema_wrapper.schematizer_client
        schematizer_client.register_schema_from_schema_json.return_value = (
            mock.MagicMock(schema_id=42))
        with mock.patch(
            "replication_handler.components.change_log_data_event_handler.open"
        ) as mock_open:
            mock_open.return_value = mock.MagicMock(spec=file)
            mock_open.return_value.__enter__.return_value.read.return_value = (
                '{"namespace": "foo", "name": "bar"}'
            )

            event_handler = ChangeLogDataEventHandler(
                db_connections=mock_db_connections,
                producer=mock.MagicMock(),
                schema_wrapper=schema_wrapper,
                stats_counter=mock.MagicMock(),
                register_dry_run=False,
                gtid_enabled=False
            )

            assert 42 == event_handler.schema_id
        schematizer_client.register_schema_from_schema_json.assert_called_once_with(
            contains_pii=False,
            namespace='foo',
            schema_json={'namespace': 'foo', 'name': 'bar'},
            source=u'bar',
            source_owner_email=u'distsys-data+changelog@yelp.com'
        )

    @mock.patch.object(ChangeLogDataEventHandler, '_handle_row')
    def test_handle_event(self, mock_row, event_handler):
        event = mock.MagicMock(schema="schema")
        event_handler.handle_event(event, "position")
        mock_row.assert_called_once_with(event_handler.schema_wrapper_entry, event, "position")

    @mock.patch(
        'replication_handler.components.change_log_data_event_handler.ChangeLogMessageBuilder',
        autospec=True
    )
    def test_handle_row_calls_ChangeLogMessageBuilder(
        self,
        ChangeLogMessageBuilder,
        event_handler,
        fake_transaction_id_schema_id
    ):
        event = mock.MagicMock(table="table")
        event_handler._handle_row("schema_wrapper_entry", event, "position")
        ChangeLogMessageBuilder.assert_called_once_with(
            "schema_wrapper_entry",
            event,
            fake_transaction_id_schema_id,
            "position",
            False
        )
