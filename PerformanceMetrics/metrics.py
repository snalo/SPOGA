from cmath import pi
from Hardware.Accumulator_TIA import Accumulator_TIA
from Hardware.BtoS import BtoS
from Hardware.MRR import MRR
from Hardware.Serializer import Serializer
from Hardware.eDram import EDram
from Hardware.ADC import ADC
from Hardware.DAC import DAC
from Hardware.PD import PD
from Hardware.TIA import TIA
from Hardware.VCSEL import VCSEL
from Hardware.io_interface import IOInterface
from Hardware.bus import Bus
from Hardware.router import Router
from Hardware.Activation import Activation
from Hardware.Adder import Adder

import math


class Metrics:

    def __init__(self):
        self.eDram = EDram()
        self.adder = Adder()
        self.adc = ADC()
        self.dac = DAC()
        self.pd = PD()
        self.tia = TIA()
        self.mrr = MRR()
        self.io_interface = IOInterface()
        self.bus = Bus()
        self.router = Router()
        self.activation = Activation()
        self.serializer = Serializer()
        self.accum_tia = Accumulator_TIA()
        self.b_to_s = BtoS()
        self.vcsel = VCSEL()
        self.laser_power_per_wavelength = 1.274274986e-3
        self.wall_plug_efficiency = 5  # 20%
        self.thermal_tuning_latency = 4000e-9
        self.photonic_adder = 1060+5.12+200 
        

    def get_hardware_utilization(self, utilized_rings, idle_rings):

        return (utilized_rings/(utilized_rings+idle_rings))*100

    def get_dynamic_energy(self, accelerator, utilized_rings):
        dynamic_energy_comp = {}
        total_energy = 0
        # * For each vdp in accelerator the number of calls gives the number of times eDRam is called
        # * The dynamic energy of ADC, DAC , MRR = no of rings utilized*their energy
        # * PD and TIA energy = vdp calls * no of vdp elements in each VDP
        dynamic_energy_comp['edram']  = 0
        dynamic_energy_comp['pd_energy']  = 0
        dynamic_energy_comp['tia_energy']  = 0
        dynamic_energy_comp['s_a_energy']  = 0
        dynamic_energy_comp['dac_energy'] = 0
        dynamic_energy_comp['adc_energy'] = 0
        dynamic_energy_comp['mrr_energy'] = 0
        total_vdp_calls = 0
        for vdp in accelerator.vdp_units_list:
            eDram_energy = vdp.calls_count*self.eDram.energy
            total_vdp_calls+=vdp.calls_count
            if accelerator.vdp_type == 'SPOGA':
                pd_energy = vdp.calls_count * vdp.get_element_count() * 3 * self.pd.energy
                tia_energy = vdp.calls_count * vdp.get_element_count() *3 * self.tia.energy
                s_a_energy = 0
            else:
                pd_energy = vdp.calls_count * vdp.get_element_count() * self.pd.energy
                tia_energy = vdp.calls_count * vdp.get_element_count() * self.tia.energy
                s_a_energy = vdp.calls_count * self.adder.energy
            dynamic_energy_comp['edram'] = dynamic_energy_comp['edram']+  eDram_energy
            dynamic_energy_comp['pd_energy'] =dynamic_energy_comp['pd_energy']+ pd_energy
            dynamic_energy_comp['tia_energy'] = dynamic_energy_comp['tia_energy']+ tia_energy
            dynamic_energy_comp['s_a_energy'] =dynamic_energy_comp['s_a_energy'] +s_a_energy

            total_energy += eDram_energy+pd_energy+tia_energy+s_a_energy


        dac_energy = self.dac.energy * utilized_rings
        adc_energy = vdp.calls_count * vdp.get_element_count() *self.adc.energy
        mrr_energy = self.mrr.energy*utilized_rings
        dynamic_energy_comp['dac_energy'] =dynamic_energy_comp['dac_energy']+ dac_energy
        dynamic_energy_comp['adc_energy'] =dynamic_energy_comp['adc_energy']+ adc_energy
        dynamic_energy_comp['mrr_energy'] =dynamic_energy_comp['mrr_energy']+ mrr_energy
        print('Dynamic Energy Components', dynamic_energy_comp)
        total_energy += adc_energy+mrr_energy+dac_energy


        print("Total VDP Calls ", total_vdp_calls)
        print("Utilized Rings", utilized_rings)
        return total_energy

    def get_total_latency(self, latencylist):
        total_latency = sum(latencylist)+self.thermal_tuning_latency
        return total_latency

    def get_static_power(self, vdp_type, unit_count, N, M):

        total_power_per_unit = 0
        total_power = 0
        vdp_power = 0

        # * adding no of comb switches  to the vdp element
        element_size = N
        elements_count = M

        if vdp_type == 'DEAPCNN':
            no_of_adc = elements_count
            no_of_dac = 2*elements_count*element_size
            no_of_pd = elements_count
            no_of_tia = elements_count
            no_of_mrr = 2*elements_count*element_size
            laser_power = self.laser_power_per_wavelength*elements_count*element_size
            power_params = {}
            power_params['adc'] = no_of_adc*self.adc.power
            power_params['dac'] = no_of_dac*self.dac.power
            power_params['pd'] = no_of_pd*self.pd.power
            power_params['tia'] = no_of_tia*self.tia.power
            power_params['mrr'] = no_of_mrr * \
                (self.mrr.power_eo+self.mrr.power_to)
            power_params['laser_power'] = laser_power
            vdp_power += no_of_adc*self.adc.power + no_of_dac*self.dac.power + self.adder.power +no_of_pd*self.pd.power + no_of_tia * \
                self.tia.power + no_of_mrr * \
                (self.mrr.power_eo+self.mrr.power_to) + \
                laser_power*self.wall_plug_efficiency



        if vdp_type == 'HOLYLIGHT':
            no_of_adc = elements_count
            no_of_dac = element_size + (elements_count*element_size)
            no_of_pd = elements_count
            no_of_tia = elements_count
            no_of_mrr = elements_count*element_size+element_size
            laser_power = self.laser_power_per_wavelength*elements_count*element_size
            power_params = {}
            power_params['adc'] = no_of_adc*self.adc.power
            power_params['dac'] = no_of_dac*self.dac.power
            power_params['pd'] = no_of_pd*self.pd.power
            power_params['tia'] = no_of_tia*self.tia.power
            power_params['mrr'] = no_of_mrr * \
                (self.mrr.power_eo+self.mrr.power_to)
            power_params['laser_power'] = laser_power

            vdp_power += no_of_adc*self.adc.power + no_of_dac*self.dac.power+self.adder.power + no_of_pd*self.pd.power + no_of_tia * \
                self.tia.power + no_of_mrr * \
                (self.mrr.power_eo+self.mrr.power_to) + \
                laser_power*self.wall_plug_efficiency

        if vdp_type == 'SPOGA':
            no_of_adc = elements_count
            no_of_dac = elements_count*element_size*8
            no_of_pd = 3 * elements_count
            no_of_tia = 3 * elements_count
            no_of_mrr = 8*elements_count*element_size
            laser_power = self.laser_power_per_wavelength
            power_params = {}
            power_params['adc'] = no_of_adc*self.adc.power
            power_params['dac'] = no_of_dac*self.dac.power
            power_params['pd'] = no_of_pd*self.pd.power
            power_params['tia'] = no_of_tia*self.tia.power
            power_params['mrr'] = no_of_mrr * \
                (self.mrr.power_eo+self.mrr.power_to)
            power_params['laser_power'] = laser_power

            vdp_power += no_of_adc*self.adc.power + no_of_dac*self.dac.power + no_of_pd*self.pd.power + no_of_tia * \
                self.tia.power + no_of_mrr * \
                (self.mrr.power_eo+self.mrr.power_to) + \
                laser_power*self.wall_plug_efficiency
            # print("VDP Power ", vdp_power)
        pheripheral_power_params = {}
        pheripheral_power_params['io'] = self.io_interface.power
        pheripheral_power_params['bus'] = self.bus.power
        pheripheral_power_params['eram'] = self.eDram.power
        pheripheral_power_params['router'] = self.router.power
        pheripheral_power_params['activation'] = self.activation.power
        total_power_per_unit += self.io_interface.power + self.activation.power + \
            self.router.power + self.bus.power + vdp_power + self.eDram.power
        total_power = total_power_per_unit*unit_count
        print("Total Power ", total_power)
        return total_power

    def get_total_area(self, TYPE, unit_count, N, M):

        pitch = 5  # um
        radius = 4.55  # um
        S_A_area = 0.00003  # mm2
        eDram_area = 0.166  # mm2
        max_pool_area = 0.00024  # mm2
        sigmoid = 0.0006  # mm2
        splitter = 0.005  # mm2
        router = 0.151 # mm2
        bus = 0.009  # mm2
        pd= 1.40625 * 1e-5  # mm2
        adc = self.adc.area  # mm2
        dac = self.dac.area  # mm2
        io_interface = 0.0244  # mm2
        serializer = 5.9 * 1e-3  # mm2
        voltage_adder = 0 #mm2
        tir = 0 #mm2
        print('Area ADC', adc)
        print('Area DAC', dac)
        if TYPE == 'HOLYLIGHT':
            print('HOLYLIGHT(MAM)')
            mrr_area = (3.14 * (radius ** 2) * 1e-6)
            dp_unit_area = mrr_area * N * M + N * mrr_area
            splitter_area = M * splitter
            pd_area = (M) * pd
            adc_area = M * adc
            dac_area = (M+1) * (N) * dac
            total_dpu_unit_area = unit_count* \
                                   (dp_unit_area + pd_area + splitter_area + adc_area + dac_area)
            total_area = total_dpu_unit_area + math.ceil(unit_count/4)*(S_A_area + eDram_area + sigmoid + router + bus + max_pool_area + io_interface)
            # print('N', N)
            # print('M', M)
            # print('S_A_area', S_A_area)
            # print('eDram_area', eDram_area)
            # print('sigmoid', sigmoid)
            # print('router', router)
            # print('bus', bus)
            # print('max_pool_area', max_pool_area)
            # print('io_interface', io_interface)
            return total_area
        elif TYPE == 'DEAPCNN':
            print('DEAPCNN(AMM)')

            mrr_area = (3.14 * (radius ** 2) * 1e-6)

            dp_unit_area = mrr_area * (2*N * M)

            splitter_area = M * splitter

            pd_area = (M) * pd

            adc_area = M * adc

            dac_area = (M) * (2*N) * dac

            total_dpu_unit_area = unit_count * \
                                  (dp_unit_area + pd_area + splitter_area + adc_area + dac_area)

            total_area = total_dpu_unit_area + math.ceil(unit_count / 4) * (
                        S_A_area + eDram_area + sigmoid + router + bus + max_pool_area + io_interface)
            # print('N', N)
            # print('M', M)
            # print('total_cnn_units_area', total_cnn_units_area)
            # print('S_A_area', S_A_area)
            # print('eDram_area', eDram_area)
            # print('sigmoid', sigmoid)
            # print('router', router)
            # print('bus', bus)
            # print('max_pool_area', max_pool_area)
            # print('io_interface', io_interface)

            return total_area

        elif TYPE == 'SPOGA':

            mrr_area = (3.14 * (radius ** 2) * 1e-6)

            dp_unit_area = mrr_area * (16 * N * M) + 4 * M

            splitter_area = M * splitter

            pd_area = (3*M) * pd

            adc_area = M * adc

            dac_area = (16*M*N)*dac

            voltage_adder_area = M*voltage_adder

            pca_area = 3*tir*M

            total_dpu_unit_area = unit_count * \
                                  (dp_unit_area + pd_area + splitter_area + adc_area + dac_area + voltage_adder_area + pca_area)

            total_area = total_dpu_unit_area + math.ceil(unit_count / 4) * (eDram_area + sigmoid + router + bus + max_pool_area + io_interface)

            return total_area
