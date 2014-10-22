from simpy.core import BoundClass
from simpy.resources import base

class SlotsPut(base.Put):
    def __init__(self, resource, slots):
        self.slots = slots
        super(SlotsPut, self).__init__(resource)

class SlotsGet(base.Get):
    def __init__(self, resource, cores):
        self.cores = cores
        super(SlotsGet, self).__init__(resource)

class Slots(base.BaseResource):
    def __init__(self, env, capacity=1):
        super(Slots, self).__init__(env)
        if capacity <= 0:
            raise ValueError('"capacity" must be > 0.')
        self._capacity = capacity
        self.slots = []

    @property
    def capacity(self):
        """The maximum capacity of the slots."""
        return self._capacity

    @property
    def available(self):
        """The number of current available slots."""
        return len(self.slots)

    put = BoundClass(SlotsPut)

    get = BoundClass(SlotsGet)

    def _do_put(self, event):
        # Deal with single entry slots
        if not isinstance(event.slots, list):
            event.slots = [event.slots]

        if len(event.slots) + self.available <= self.capacity:
            self.slots.extend(event.slots)
            event.succeed()
        # TODO: What about the "else" case?

    def _do_get(self, event):

        if event.cores > self.available:
            raise ValueError("Can't get more than capacity allows.")

        if self.slots >= self.available:
            result = self.slots[-event.cores:]
            del self.slots[-event.cores:]
            event.succeed(result)


if __name__ == '__main__':
    pass
