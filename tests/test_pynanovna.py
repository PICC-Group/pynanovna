import pytest
from ..src.pynanovna.pynanovna import VNA

@pytest.fixture
def vna():
    """Fixture to initialize VNA for each test."""
    return VNA()

def test_initialization(vna):
    """Test VNA initialization and connected status."""
    assert vna.connected, "VNA should be connected after initialization"

def test_set_sweep(vna):
    """Test setting the sweep parameters."""
    vna.set_sweep(1e6, 1e9, 101)  # Start, stop, and points
    assert vna.sweep_interval == (1e6, 1e9)
    assert vna.sweep_points == 101

def test_sweep(vna):
    """Test running a sweep."""
    vna.set_sweep(1e6, 1e9, 101)
    s11, s21, frequencies = vna.sweep()
    assert len(s11) == 101
    assert len(s21) == 101
    assert len(frequencies) == 101

def test_stream(vna):
    """Test continuous data streaming."""
    vna.set_sweep(1e6, 1e9, 101)
    generator = vna.stream()
    s11, s21, frequencies = next(generator)
    assert len(s11) == 101
    assert len(s21) == 101
    assert len(frequencies) == 101

def test_stream_to_csv(vna, tmp_path):
    """Test streaming data to a CSV file."""
    filename = tmp_path / "output.csv"
    vna.stream_to_csv(str(filename), nr_sweeps=1)
    with open(filename, "r") as f:
        lines = f.readlines()
    assert len(lines) > 3  # Header plus at least a few data lines

def test_calibration_steps(vna):
    """Test calibration steps."""
    vna.set_sweep(1e6, 1e9, 101)
    for step in ["short", "open", "load", "isolation", "through"]:
        vna.calibration_step(step)
        assert vna.calibration.isCalculated, f"Calibration should be calculated after {step} step"

def test_save_calibration(vna, tmp_path):
    """Test saving calibration data."""
    filename = tmp_path / "calibration.cal"
    vna.set_sweep(1e6, 1e9, 101)
    vna.calibration_step("short")
    vna.calibrate()
    assert vna.save_calibration(str(filename)), "Calibration should be saved successfully"

def test_load_calibration(vna, tmp_path):
    """Test loading calibration data."""
    filename = tmp_path / "calibration.cal"
    vna.set_sweep(1e6, 1e9, 101)
    vna.calibration_step("short")
    vna.calibrate()
    vna.save_calibration(str(filename))
    vna.load_calibration(str(filename))
    assert vna.calibration.is_valid_1_port(), "Calibration should be valid after loading"

def test_vna_info(vna):
    """Test retrieving VNA information."""
    info = vna.info()
    assert "Serial Number" in info and "Version" in info, "Info should contain serial number and version"

def test_disconnect(vna):
    """Test VNA disconnection."""
    vna.kill()
    assert not vna.is_connected(), "VNA should be disconnected"
