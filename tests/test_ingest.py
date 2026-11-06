"""T1, T5 (phần đọc IFC) và xử lý đơn vị DXF."""
import ezdxf
import pytest

from src.config import DataError
from src.ingest.dxf import load_dxf, unit_factor
from src.ingest.ifc import load_ifc


def test_t1_dxf_readable_no_audit_errors(root):
    for name in ("sample-floor-1.dxf", "sample-floor-2.dxf"):
        doc = ezdxf.readfile(root / "samples" / name)
        assert doc.units == 6                      # mét
        assert len(doc.audit().errors) == 0
        src = load_dxf(root / "samples" / name)
        assert src.factor == 1.0 and src.warnings == []


def test_dxf_unitless_uses_fallback_and_warns(tmp_path):
    doc = ezdxf.new("R2010")
    doc.units = 0                                  # unitless
    doc.saveas(tmp_path / "u.dxf")
    src = load_dxf(tmp_path / "u.dxf", fallback_unit="mm")
    assert src.factor == 1e-3
    assert any("fallback_unit" in w for w in src.warnings)


def test_unit_factor_unsupported_codes_use_fallback():
    for code in (0, 8, 9, 21, 24):                 # ezdxf.conversion_factor ném TypeError với các mã này
        f, w = unit_factor(code, "m")
        assert f == 1.0 and w


def test_ifc_unit_scale_metres(root):
    src = load_ifc(root / "samples" / "sample-building.ifc")
    assert src.unit_scale == 1.0 and src.schema == "IFC4"


def test_missing_files_raise_data_error(tmp_path):
    with pytest.raises(DataError):
        load_dxf(tmp_path / "nope.dxf")
    with pytest.raises(DataError):
        load_ifc(tmp_path / "nope.ifc")
