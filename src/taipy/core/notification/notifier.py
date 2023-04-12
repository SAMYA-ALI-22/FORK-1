# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Dict, List, Optional

from .event import Event, EventEntityType, EventOperation
from .registration import Registration
from .topic import Topic


class Notifier:
    _registrations: Dict[Topic, List[Registration]] = {}  # What if this is a dictionary instead?

    @classmethod
    def register(
        cls,
        entity_type: Optional[str],
        entity_id: Optional[str],
        operation: Optional[str],
        attribute_name: Optional[str],
    ) -> Registration:
        # TODO: the signature should all parameter be string??
        registration = Registration(entity_type, entity_id, operation, attribute_name)

        if registrations := cls._registrations.get(registration.topic, None):
            registrations.append(registration)
        else:
            cls._registrations[registration.topic] = [registration]

        return registration

    @classmethod
    def unregister(cls, registration: Registration):
        if registrations := cls._registrations.get(registration.topic, None):
            registrations.remove(registration)
            if len(registrations) == 0:
                del cls._registrations[registration.topic]

    @classmethod
    def publish(cls, event: Event):
        generated_matched_topics_with_event = cls.generate_topics_from_event(event)

        for topic in generated_matched_topics_with_event:
            if registrations := cls._registrations.get(topic, None):
                for registration in registrations:
                    registration.queue.put(event)

    @staticmethod
    def generate_topics_from_event(event: Event):
        # can this be improved by caching?
        TOPIC_ATTRIBUTES_TO_SET_NONE: list = [
            [
                "entity_type",
                "entity_id",
                "operation",
                "attribute_name",
            ],
            [
                "entity_id",
                "operation",
                "attribute_name",
            ],
            [
                "entity_type",
                "entity_id",
            ],
            [
                "entity_type",
                "entity_id",
                "attribute_name",
            ],
            [
                "entity_type",
                "entity_id",
                "operation",
            ],
            [
                "entity_id",
                "attribute_name",
            ],
            [
                "entity_id",
                "operation",
            ],
            [
                "attribute_name",
            ],
            ["operation"],
            [
                "entity_type",
                "entity_id",
            ],
            [
                "entity_id",
            ],
            [],
        ]

        def generate_topic_parameters_from_event(event: Event):
            return {
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "operation": event.operation,
                "attribute_name": event.attribute_name,
            }

        topics = []

        for topic_attributes_to_set_None in TOPIC_ATTRIBUTES_TO_SET_NONE:
            topic_parameters = generate_topic_parameters_from_event(event)
            for topic_attribute in topic_attributes_to_set_None:
                topic_parameters[topic_attribute] = None
            topics.append(Topic(**topic_parameters))
        return topics
