
## SPOGA - Scaling Analog Photonic Accelerators for Byte-Size, Integer General Matrix Multiply (GEMM) Kernels

### Publication ArXiv Preprint
https://arxiv.org/abs/2407.06134

Publication can be cited: 

```bash
@inproceedings{Alo_2024,
   title={Scaling Analog Photonic Accelerators for Byte-Size, Integer General Matrix Multiply (GEMM) Kernels},
   url={http://dx.doi.org/10.1109/ISVLSI61997.2024.00080},
   DOI={10.1109/isvlsi61997.2024.00080},
   booktitle={2024 IEEE Computer Society Annual Symposium on VLSI (ISVLSI)},
   publisher={IEEE},
   author={Alo, Oluwaseun Adewunmi and Vatsavai, Sairam Sri and Thakkar, Ishan},
   year={2024},
   month=jul, pages={409–414} 
   }
```


The SPOGA accelerator used the B_ONN_SIM (BINARY Optical Neural Network Simulator) which is a transaction-level, event-driven python-based simulator for evaluation of Binary optical neural network accelerators for various Binary Neural Network models. 

Follow the Guide to use: 
### Installation and Execution

    git clone https://github.com/Sairam954/B_ONN_SIM.git
    python main.py

### Bibtex

Please cite if you use B_ONN_SIM

```bash
@misc{OXBNNISQED2023,
  doi = {10.48550/ARXIV.2302.06405},
  url = {https://arxiv.org/abs/2302.06405},
  author = {Vatsavai, Sairam Sri and Karempudi, Venkata Sai Praneeth and Thakkar, Ishan},
  keywords = {Hardware Architecture (cs.AR), Computer Vision and Pattern Recognition (cs.CV), Machine Learning (cs.LG), FOS: Computer and information sciences, FOS: Computer and information sciences},
  title = {An Optical XNOR-Bitcount Based Accelerator for Efficient Inference of Binary Neural Networks},
  publisher = {arXiv},
  year = {2023},
  copyright = {Creative Commons Attribution 4.0 International}
}

```

### Video Tutorial by Dr. Sairam
https://www.youtube.com/watch?v=X6yifdEB7xU

### Accelerator Configuration 

The accelerator configuration can be provided in main.py file. The configuration dictionary looks like below:
``` bash
ACCELERATOR = [
{
    ELEMENT_SIZE: 249, # The supported dot product size of the processing unit, generally equal to number of wavelengths multiplexed in weight bank/activation bank 
    ELEMENT_COUNT: 16, # Number of parallel dot products that can be performed by one processing unit, generally equal to the number of output waveguides in a processing unit  
    UNITS_COUNT: 150, # Number of processing unit present in an accelerator
    RECONFIG: [], # Useful if the processing unit element size can be reconfigured according to the convolution computation need
    VDP_TYPE: "MAW", # More information abour vector dot product can be found in our paper ([https://ieeexplore.ieee.org/abstract/document/9852767]
    NAME: "SPOGA", # Name of the accelerator 
    ACC_TYPE: "SPOGA_1", # Accelerator Type for example, ANALOG etc. This parameter helps in evaluation of performance metrics based on accelerator
    PRECISION: 8, # The bit precision supported  by the accelerator, this value along with ***accelerator_required_precision*** determines whether bit-slicing needs to be implemented
    BITRATE: 1, # The bit rate of the accelerator 
}
]
```
### SPOGA Accelerator
The below image shows SPOGA accelerator processing unit.
![The SPOGA Architecture](/assets/spoga_architecture.png "The SPOGA Architecture")

### Binary_ONN_Simulator Project Structure 
``` bash
│   constants.py
│   main.py - *Runs the simulator and allows users to change the inputs according to the accelerator* 
│   README.md
│   requirements.txt
│   visualization.py - *Plots the performance metrics like FPS, FPS/W etc of various accelerators on single barplot and also provides information of the best performing accelerator* 
│   __init__.py
│
| *Script to generate model files ->(https://github.com/Sairam954/CNN_Model_Layer_Information_Generator)*
├───CNNModels - *Folder contains various CNN models available for performing simulations. 
│   │   GoogLeNet.csv
│   │   MobileNet_V2.csv
│   │   ResNet50.csv
│   │   ShuffleNet_V2.csv
│   │   VGG16.csv
│   │
│   └───Sample
│           ResNet50.csv
│
├───Controller - *This contains the logic for scheduling the convolutions and corresponding dot product operations on to the accelerator hardware*
│   │   controller.py
│   │   __init__.py
│   │
│   └───__pycache__
│           controller.cpython-310.pyc
│           controller.cpython-38.pyc
│           __init__.cpython-310.pyc
│           __init__.cpython-38.pyc
│
├───Exceptions - *Accelerator Custom Exceptions*
│   │   AcceleratorExceptions.py
│   │
│   └───__pycache__
│           AcceleratorExceptions.cpython-310.pyc
│           AcceleratorExceptions.cpython-38.pyc
│
├───Hardware - *Different classes corresponding to the accelerator*
│   │   Accelerator.py
│   │   Accumulator_TIA.py
│   │   Activation.py
│   │   ADC.py
│   │   Adder.py
│   │   BtoS.py
│   │   bus.py
│   │   DAC.py
│   │   eDram.py
│   │   io_interface.py
│   │   LightBulbVDP.py
│   │   MRR.py
│   │   MRRVDP.py
│   │   PD.py
│   │   Pheripheral.py
│   │   Pool.py
│   │   RobinVDP.py
│   │   router.py
│   │   Serializer.py
│   │   stochastic_MRRVDP.py
│   │   TIA.py
│   │   VCSEL.py
│   │   VDP.py
│   │   vdpelement.py
│   │   __init__.py  
│
└───PerformanceMetrics
│   │   metrics.py - *Class to calculate various peformance metrics like FPS, FPS/W and FPS/W/mm2*
│ 
│
├───Plots - *Folder containing the plots produced by visualization.py*
│   │       FPS_(Log_Scale).png
│   │
│   └───Sample
├───Result
│   └───ISQED - *Simulation Result of various Binary Neural Network Accelerator*

```

### Simulation Result CSV:
After the simulations are completed, the results are stored in the results dir

The performance metrics are calculated by using PeformanceMetrics/metrics.py, currently it provides the above values. Users can change the file to reflect their accelerator components energy and power parameters.  

### Evaluation Visualization:
The visualization.py can take the generated simulation csv and plot barplot for the results. It also prints useful information in the console about the top two accelerators. 
![image](/Plots/FPS_(Log_Scale).png "FPS_(Log_Scale)")