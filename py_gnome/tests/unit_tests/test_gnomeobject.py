"""
Test if this is how we want id property of
object that inherits from GnomeId to behave
"""
from datetime import datetime, timedelta
import pytest
import copy

from uuid import uuid1
from gnome.gnomeobject import GnomeId
from gnome import (environment,
                   movers,
                   outputters,
                   spill)
from gnome.model import Model
from gnome.environment import Waves, Wind, Water
from gnome.weatherers import Evaporation, NaturalDispersion


def test_exceptions():
    with pytest.raises(AttributeError):
        go = GnomeId()
        print '\n id exists: {0}'.format(go.id)  # calls getter, assigns an id
        go.id = uuid1()


def test_copy():
    go = GnomeId()
    go_c = copy.copy(go)
    assert go.id != go_c.id
    assert go is not go_c


def test_deepcopy():
    go = GnomeId()
    go_c = copy.deepcopy(go)
    assert go.id != go_c.id
    assert go is not go_c


'''
test 'name' is an input for all base classes
'''
base_class = [(environment.Environment, ()),
              (movers.Mover, ()),
              (outputters.Outputter, ()),
              (spill.Release, (10,)),
              (spill.Spill, (spill.Release(0),))
              ]


@pytest.mark.parametrize("b_class", base_class)
def test_set_name(b_class):
    name = "name_{0}".format(uuid1())
    class_ = b_class[0]
    inputs = b_class[1]
    obj = class_(*inputs, name=name)
    assert obj.name == name

    obj.name = obj.__class__.__name__
    assert obj.name == obj.__class__.__name__


t = datetime(2015, 1, 1, 12, 0)


@pytest.mark.parametrize(("obj", "objvalid"),
                         [(Wind(timeseries=[(t, (0, 1)),
                                            (t + timedelta(10), (0, 2))],
                                units='m/s'), True),
                          (Evaporation(), False),
                          (NaturalDispersion(), False)])
def test_base_validate(obj, objvalid):
    '''
    base validate checks wind/water/waves objects are not None. Check these
    primarily for weatherers.
    '''
    (out, isvalid) = obj.validate()
    print out
    print isvalid
    assert isvalid is objvalid
    assert len(out) > 0


def test_make_default_refs():
    '''
    ensure make_default_refs is a thread-safe operation
    once object is instantiated, object.make_default_refs is an attribute of
    instance
    '''
    model = Model()
    wind = Wind(timeseries=[(t, (0, 1))], units='m/s')
    water = Water()

    waves = Waves(name='waves')
    waves.make_default_refs = False
    waves1 = Waves(name='waves1')
    model.environment += [wind,
                          water,
                          waves,
                          waves1]

    # waves1 should get auto hooked up/waves2 should not
    model.step()
    assert waves.wind is None
    assert waves.water is None
    assert waves1.wind is wind
    assert waves1.water is water
