from __future__ import annotations

import logging
from typing import Optional

try:
    from smbus2 import SMBus
except ImportError:  # pragma: no cover
    SMBus = None  # type: ignore

from ..models import BatteryStatus

LOGGER = logging.getLogger(__name__)


class WittyPiController:
    def __init__(self, i2c_address: int, bus: int = 1) -> None:
        self.address = i2c_address
        self.bus_id = bus

    def read_battery_status(self) -> Optional[BatteryStatus]:
        if SMBus is None:
            LOGGER.debug("smbus2 unavailable; skipping Witty Pi telemetry")
            return None
        try:
            with SMBus(self.bus_id) as bus:
                raw = bus.read_i2c_block_data(self.address, 0, 16)
        except FileNotFoundError:
            LOGGER.warning("I2C bus %s unavailable", self.bus_id)
            return None
        except OSError as exc:
            LOGGER.error("Unable to query Witty Pi: %s", exc)
            return None

        if len(raw) < 12:
            LOGGER.error("Unexpected Witty Pi register payload: %s", raw)
            return None

        input_v = raw[0] + raw[1] / 100.0
        output_v = raw[2] + raw[3] / 100.0
        output_c = raw[4] + raw[5] / 100.0
        power_mode = raw[6]
        low_voltage_flag = raw[8]
        last_reason = raw[11]

        return BatteryStatus(
            input_voltage=input_v,
            output_voltage=output_v,
            output_current=output_c,
            is_external_power=(power_mode == 0),
            is_low_voltage_shutdown=bool(low_voltage_flag),
            last_action_code=last_reason,
        )
