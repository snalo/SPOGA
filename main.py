from os.path import isfile, join
from os import listdir
import logging as logging
import pandas as pd
import math
from Controller.controller import Controller
from Hardware.vdpelement import VDPElement
from constants import *
from PerformanceMetrics.metrics import Metrics
from Hardware.VDP import VDP
from Hardware.Pool import Pool
from Hardware.stochastic_MRRVDP import Stocastic_MRRVDP
from Hardware.MRRVDP import MRRVDP
from Hardware.Adder import Adder
from Hardware.Accelerator import Accelerator
from Exceptions.AcceleratorExceptions import VDPElementException
from ast import Str
import os.path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))


logger = logging.getLogger("__main__")
logger.setLevel(logging.INFO)

# * Input model files column headers constants
LAYER_TYPE = "name"
MODEL_NAME = "model_name"
KERNEL_DEPTH = "kernel_depth"
KERNEL_HEIGHT = "kernel_height"
KERNEL_WIDTH = "kernel_width"
TENSOR_COUNT = "tensor_count"
INPUT_SHAPE = "input_shape"
OUTPUT_SHAPE = "output_shape"
TENSOR_SHAPE = "tensor_shape"
INPUT_HEIGHT = "input_height"
INPUT_WIDTH = "input_width"
INPUT_DEPTH = "input_depth"
OUTPUT_HEIGHT = "output_height"
OUTPUT_WIDTH = "output_width"
OUTPUT_DEPTH = "output_depth"


# * performance metrics
HARDWARE_UTILIZATION = "hardware_utilization"
TOTAL_LATENCY = "total_latency"
TOTAL_DYNAMIC_ENERGY = "total_dynamic_energy"
TOTAL_STATIC_POWER = "total_static_power"
CONFIG = "config"
AUTO_RECONFIG = "auto_reconfig"
SUPPORTED_LAYER_LIST = "supported_layer_list"
AREA = "area"
FPS = "fps"
FPS_PER_AREA = "fps_per_area"
FPS_PER_W = "fps_per_w"
FPS_PER_W_PER_AREA = "fps_per_w_per_area"
EDP = "edp"
CONV_TYPE = "conv_type"
VDP_TYPE = 'vdp_type'
NAME = 'name'
POWER = 'power'

# * VDP element constants
ring_radius = 4.55E-6
pitch = 5E-6
vdp_units = []
# * ADC area and power changes with BR {BR: {area: , power: }}}
#TODO update the correct area and power values
adc_area_power = {
    1: {AREA: 2, POWER: 2.55},
    5: {AREA: 21, POWER: 11},
    10: {AREA: 103, POWER: 30}
}
#Area in mm2 and power in mW
dac_area_power = {
    1: {AREA: 0.00007, POWER: 0.12},
    5: {AREA: 0.06, POWER: 26},
    10: {AREA: 0.06, POWER: 30}
}
# PCA_ACC_Count = 10

def run(modelName, cnnModelDirectory, accelerator_config, required_precision=8):

    print("The Model being Processed---->", modelName)
    print("Simulator Execution Begin")
    print("Start Creating Accelerator")

    run_config = accelerator_config

    result = {}
    print("Accelerator configuration", run_config)
    # * Declaration of all the objects needed for excuting a CNN model on to the accelerator to find latency and hardware utilization
    accelerator = Accelerator()
    adder = Adder()
    pool = Pool()
    

    controller = Controller()
    metrics = Metrics()

    # * Creating MRR VDP units with the vdp configurations and adding it to accelerator
    for vdp_config in run_config:
        vdp_type = vdp_config[VDP_TYPE]
        accelerator.set_vdp_type(vdp_type)
        # accelerator.set_acc_type(vdp_config.get(ACC_TYPE))
        
        # * Peripheral Parameters assigning
        adder.latency = (1/vdp_config.get(BITRATE))*1e-9
        accelerator.add_pheripheral(ADDER, adder)
        
        accelerator.add_pheripheral(POOL, pool)
        for vdp_no in range(vdp_config.get(UNITS_COUNT)):
            vdp = MRRVDP(ring_radius, pitch, vdp_type,
                         vdp_config.get(SUPPORTED_LAYER_LIST), vdp_config.get(BITRATE))
            for vdp_element in range(vdp_config.get(ELEMENT_COUNT)):
                vdp_element = VDPElement(vdp_config[ELEMENT_SIZE], vdp_config.get(
                    RECONFIG), vdp_config.get(AUTO_RECONFIG), vdp_config.get(PRECISION))
                vdp.add_vdp_element(vdp_element)
            # * Need to call set vdp latency => includes latency of prop + tia latency + pd latency + etc
            vdp.set_vdp_latency()
            accelerator.add_vdp(vdp)
    print("ACCELERATOR CREATED WITH THE GIVEN CONFIGURATION ")

    # # * Read Model file to load the dimensions of each layer
    nnModel = pd.read_csv(cnnModelDirectory+modelName)
    nnModel = nnModel.astype({"model_name": str, 'name': str, 'kernel_depth': int, 'kernel_height': int, 'kernel_width': int,	'tensor_count': int, 'input_shape': str,
                             'output_shape': str, 'tensor_shape': str,	'input_height': int,	'input_width': int, 'input_depth': int, 'output_height': int, 'output_width': int, 'output_depth': int})

    # # * filter specific layers for debugging
    # nnModel = nnModel.drop(nnModel[nnModel.name == "DepthWiseConv"].index)
    # nnModel = nnModel.drop(nnModel[nnModel.name == "Conv2D"].index)
    # nnModel = nnModel.drop(nnModel[nnModel.name == "PointWiseConv"].index)
    # nnModel = nnModel.drop(nnModel[nnModel.name == "Dense"].index)
    # nnModel = nnModel.drop(nnModel[nnModel.name == "MaxPooling2D"].index)

    accelerator.reset()
    total_latency = []
    vdp_ops = []
    vdp_sizes = []
    for idx in nnModel.index:
        accelerator.reset()
        layer_type = nnModel[LAYER_TYPE][idx]
        model_name = nnModel[MODEL_NAME][idx]
        kernel_depth = nnModel[KERNEL_DEPTH][idx]
        kernel_width = nnModel[KERNEL_WIDTH][idx]
        kernel_height = nnModel[KERNEL_HEIGHT][idx]
        tensor_count = nnModel[TENSOR_COUNT][idx]
        input_shape = nnModel[INPUT_SHAPE][idx]
        output_shape = nnModel[OUTPUT_SHAPE][idx]
        tensor_shape = nnModel[TENSOR_SHAPE][idx]
        input_height = nnModel[INPUT_HEIGHT][idx]
        input_width = nnModel[INPUT_WIDTH][idx]
        input_depth = nnModel[INPUT_DEPTH][idx]
        output_height = nnModel[OUTPUT_HEIGHT][idx]
        output_width = nnModel[OUTPUT_WIDTH][idx]
        output_depth = nnModel[OUTPUT_DEPTH][idx]
        # * debug statments to be deleted
        # print('Layer Name  ;', layer_type)
        # print('Kernel Height', kernel_height,'Kernel width',kernel_width, 'Kernel Depth', kernel_depth)

        # * VDP size and Number of VDP operations per layer
        vdp_size = kernel_height*kernel_width*kernel_depth
        no_of_vdp_ops = output_height*output_depth*output_width

        # * Estimate the additional vdp operations to achieve the required precision in Analog Accelerators
        available_precision = accelerator.vdp_units_list[ZERO].vdp_element_list[ZERO].precision
        if available_precision < required_precision:
            required_precision_multiplier = (math.ceil(required_precision/available_precision))**2
        else:
            required_precision_multiplier = 1
        no_of_vdp_ops = no_of_vdp_ops*required_precision_multiplier
        # print('No Of VDP Ops', no_of_vdp_ops)
        # * Latency Calculation of the VDP operations
        layer_latency = 0
        # * Handles pooling layers and sends the requests to pooling unit
        if layer_type == 'MaxPooling2D':
            pooling_request = output_depth*output_height*output_width
            pool_latency = accelerator.pheripherals[POOL].get_request_latency(
                pooling_request)
            layer_latency = pool_latency
        else:
            # * other layers are handled here
            # * if VDP_type = MAM then the inputs are shared so need to process tensor by tensor rather than whole layer VDP operations
            # print("MAM type architecture ")
            vdp_per_tensor = int(no_of_vdp_ops/tensor_count)
            # print("Total tensor_count Ops ", tensor_count)
            # print("VDP per Tensor ", vdp_per_tensor)
            # print("Tensor Count ", tensor_count)
            for tensor in range(0, tensor_count):
                layer_latency += controller.get_convolution_latency(
                    accelerator, vdp_per_tensor, vdp_size)
                # print('Tensor', tensor)
                accelerator.reset()
                # print("Layer latency", layer_latency)

            # print('Layer Latency ',layer_latency)
        total_latency.append(layer_latency)
        vdp_ops.append(no_of_vdp_ops)
        vdp_sizes.append(vdp_size)
    # print("No od VDPs", vdp_ops)
    # print("VDP size", vdp_sizes)
    # print("Latency  =",total_latency)
    run_config = run_config[0]
    running_br = run_config[BITRATE]
    metrics.adc.area = adc_area_power[running_br][AREA]
    metrics.adc.power = adc_area_power[running_br][POWER]
    metrics.dac.area = dac_area_power[running_br][AREA]
    metrics.dac.power = dac_area_power[running_br][POWER]

    total_latency = sum(total_latency)
    hardware_utilization = metrics.get_hardware_utilization(
        controller.utilized_rings, controller.idle_rings)
    dynamic_energy_w = metrics.get_dynamic_energy(
        accelerator, controller.utilized_rings)
    static_power_w = metrics.get_static_power(vdp_type, run_config[UNITS_COUNT],run_config[ELEMENT_SIZE],run_config[ELEMENT_COUNT])

    area = 0
    fps = (1 / total_latency)
    power = (dynamic_energy_w / total_latency) + static_power_w
    fps_per_w = fps / power
    print("vdp type", vdp_type, 'UNITS_COUNT', run_config[UNITS_COUNT], 'N',run_config[ELEMENT_SIZE],'M',run_config[ELEMENT_COUNT])
    area = metrics.get_total_area(vdp_type, run_config[UNITS_COUNT],run_config[ELEMENT_SIZE],run_config[ELEMENT_COUNT])
    print("Area_pre", area)
    fps_per_area = fps/area
    fps_per_w_area = fps_per_w / area
    # print("Area :", area)
    print("Total Latency ->", total_latency)
    print("FPS ->", fps)
    print("FPS/W  ->", fps_per_w)
    print("FPS/Area  ->", fps_per_area)
    print("FPS/W/Area  ->", fps_per_w_area)

    result[NAME] = accelerator_config[0][NAME]
    result['Model_Name'] = modelName.replace(".csv", "")
    result[CONFIG] = run_config
    result[HARDWARE_UTILIZATION] = hardware_utilization
    result[TOTAL_LATENCY] = total_latency
    result[FPS] = fps
    result[TOTAL_DYNAMIC_ENERGY] = dynamic_energy_w
    result[TOTAL_STATIC_POWER] = static_power_w
    result['Total Power'] = power
    result[AREA] = area
    print("Area", area)
    result[FPS_PER_W] = fps_per_w
    result[FPS_PER_AREA] = fps_per_area
    result[FPS_PER_W_PER_AREA] = fps_per_w_area
    return result

 # * GIVE CONFIGURATION FOR THE ACCELERATOR HERE

accelerator_required_precision = 4

SPOGA_1 = [{ELEMENT_SIZE: 249, ELEMENT_COUNT: 16, UNITS_COUNT: 150, RECONFIG: [
], VDP_TYPE:'SPOGA', NAME:'SPOGA_1', PRECISION:8, BITRATE: 1}]
SPOGA_5 = [{ELEMENT_SIZE: 187, ELEMENT_COUNT: 16, UNITS_COUNT: 5, RECONFIG: [
], VDP_TYPE:'SPOGA', NAME:'SPOGA_5', PRECISION: 8, BITRATE: 5}]
SPOGA_10 = [{ELEMENT_SIZE: 160, ELEMENT_COUNT: 16, UNITS_COUNT: 4, RECONFIG: [
], VDP_TYPE:'SPOGA', NAME:'SPOGA_10', PRECISION:8, BITRATE: 10}]
DEAPCNN_1 = [{ELEMENT_SIZE: 36, ELEMENT_COUNT: 36, UNITS_COUNT: 215, RECONFIG: [
], VDP_TYPE:'DEAPCNN', NAME:'DEAPCNN_1', PRECISION:4, BITRATE: 1}]
DEAPCNN_5 = [{ELEMENT_SIZE: 15, ELEMENT_COUNT: 15, UNITS_COUNT: 47, RECONFIG: [
], VDP_TYPE:'DEAPCNN', NAME:'DEAPCNN_5', PRECISION:4, BITRATE: 5}]
DEAPCNN_10 = [{ELEMENT_SIZE: 12, ELEMENT_COUNT: 12, UNITS_COUNT: 13, RECONFIG: [
], VDP_TYPE:'DEAPCNN', NAME:'DEAPCNN_10', PRECISION:4, BITRATE: 10}]
HOLYLIGHT_1 = [{ELEMENT_SIZE: 43, ELEMENT_COUNT: 43, UNITS_COUNT: 180, RECONFIG: [
], VDP_TYPE:'HOLYLIGHT', NAME:'HOLYLIGHT_1', PRECISION:4, BITRATE: 1}]
HOLYLIGHT_5 = [{ELEMENT_SIZE: 21, ELEMENT_COUNT: 21, UNITS_COUNT: 35, RECONFIG: [
], VDP_TYPE:'HOLYLIGHT', NAME:'HOLYLIGHT_5', PRECISION:4, BITRATE: 5}]
HOLYLIGHT_10 = [{ELEMENT_SIZE: 17, ELEMENT_COUNT: 17, UNITS_COUNT: 9, RECONFIG: [
], VDP_TYPE:'HOLYLIGHT', NAME:'HOLYLIGHT_10', PRECISION:4, BITRATE: 10}]

tpc_list = [SPOGA_1, SPOGA_5, SPOGA_10, DEAPCNN_1, DEAPCNN_5, DEAPCNN_10, HOLYLIGHT_1, HOLYLIGHT_5, HOLYLIGHT_10]
# tpc_list = [SPOGA_5, SPOGA_10, DEAPCNN_5, DEAPCNN_10, HOLYLIGHT_5, HOLYLIGHT_10]
# tpc_list = [SPOGA_1, HOLYLIGHT_1, DEAPCNN_1]
print("Required Precision ", accelerator_required_precision)
cnnModelDirectory = "./CNNModels/"
modelList = [f for f in listdir(
    cnnModelDirectory) if isfile(join(cnnModelDirectory, f))]

 # * TO RUN SPECIFIC MODELS USE THE BELOW LIST
modelList = ['MobileNet_V2.csv','ShuffleNet_V2.csv','ResNet50.csv', 'GoogLeNet.csv']
# modelList = ['GoogLeNet.csv']
system_level_results = []
for tpc in tpc_list:
    for modelName in modelList:
        print("Model being Processed ", modelName)
        system_level_results.append(
            run(modelName, cnnModelDirectory, tpc, accelerator_required_precision))
sys_level_results_df = pd.DataFrame(system_level_results)
sys_level_results_df.to_csv('Result/ALL_DAC_M_EL_16.csv')