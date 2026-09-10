from . import _mx_sys
from . import _mx_classes

class _c_VA_US_S(_mx_sys.BaseModel):

    def __init__(self):

        # modelx variables
        self._parent = None
        self._model = self
        self._name = "VA_US_S"

        # Space assignments
        self.Data = _mx_classes._c_Data(self)
        self.Projection = _mx_classes._c_Projection(self)
        self._mx_spaces = {
            'Data': self.Data,
            'Projection': self.Projection
        }


        self._mx_load_io()

    def _mx_assign_refs(self, io_data, pickle_data):

        pass


mx_model = VA_US_S = _c_VA_US_S()
