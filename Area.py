from PerformanceMetrics.metrics import Metrics

metrics = Metrics()
AREA = "area"
POWER = "power"
adc_area_power = {
    1: {AREA: 2, POWER: 2.55},
    5: {AREA: 21, POWER:11},
    10: {AREA: 103, POWER: 30}
}
#Area in mm2 and power in mW
dac_area_power = {
    1: {AREA: 0.00007, POWER: 0.12},
    5: {AREA: 0.06, POWER: 26},
    10: {AREA: 0.06, POWER: 30}
}
# ANALOG_ACCELERATOR = [{ELEMENT_SIZE: 4, ELEMENT_COUNT: 33, UNITS_COUNT: 200, RECONFIG: [
# ], VDP_TYPE:'AMM', NAME:'DEAPCNN', ACC_TYPE:'ANALOG', PRECISION:4, BITRATE: 1}]
# ANALOG_ACCELERATOR = [{ELEMENT_SIZE: 36, ELEMENT_COUNT: 36, UNITS_COUNT: 200, RECONFIG: [
# ], VDP_TYPE:'AMM', NAME:'HOLYLIGHT', ACC_TYPE:'ANALOG', PRECISION:4, BITRATE: 1}]
# ANALOG_ACCELERATOR = [{ELEMENT_SIZE: 43, ELEMENT_COUNT: 43, UNITS_COUNT: 200, RECONFIG: [
# ], VDP_TYPE:'AMM', NAME:'SPOGA_10', ACC_TYPE:'ANALOG', PRECISION:4, BITRATE: 1}]
# area = metrics.get_total_area(vdp_type, accelearator_config[UNITS_COUNT], 0, accelearator_config[ELEMENT_SIZE],
#                                accelearator_config[ELEMENT_COUNT], 0, 0, accelearator_config[RECONFIG],
#                                accelearator_config[ACC_TYPE])
running_br = 10
metrics.dac.area = dac_area_power[running_br][AREA]
metrics.adc.area = adc_area_power[running_br][AREA]
area = metrics.get_total_area('SPOGA',4, 160, 16) #Target Area = 55409
print("Area_per_unit_SPOGA", area)

area = metrics.get_total_area('HOLYLIGHT',9, 17,17)
print("Area_per_unit_HOLYLIGHT", area)

area = metrics.get_total_area('DEAPCNN',13, 12, 12)
print("Area_per_unit_DEAPCNN", area)
