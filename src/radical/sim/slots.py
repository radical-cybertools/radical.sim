from simpy.core import BoundClass
from simpy.resources import base

class SlotsPut(base.Put):
    def __init__(self, resource, items):
        self.items = items
        super(SlotsPut, self).__init__(resource)

class SlotsGet(base.Get):
    def __init__(self, resource, amount):
        self.amount = amount
        super(SlotsGet, self).__init__(resource)

class Slots(base.BaseResource):
    def __init__(self, env, capacity=1):
        super(Slots, self).__init__(env)
        if capacity <= 0:
            raise ValueError('"capacity" must be > 0.')
        self._capacity = capacity
        self.items = []

    @property
    def capacity(self):
        """The maximum capacity of the slots."""
        return self._capacity

    @property
    def available(self):
        """The number of current available slots."""
        return len(self.items)

    put = BoundClass(SlotsPut)

    get = BoundClass(SlotsGet)

    def _do_put(self, event):
        # Deal with single entry slots
        if not isinstance(event.items, list):
            event.items = [event.items]

        if len(event.items) + self.available <= self.capacity:
            self.items.extend(event.items)
            event.succeed()
        # TODO: What about the "else" case?

    def _do_get(self, event):

        if event.amount > self.available:
            raise ValueError("Can't get more than capacity allows.")

        if self.items >= self.available:
            result = self.items[:event.amount]
            del self.items[:event.amount]
            event.succeed(result)

