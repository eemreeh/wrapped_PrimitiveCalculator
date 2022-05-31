
  
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, with_timeout
import random
from encoder import Encoder_calc

@cocotb.test()
async def test_start(dut):
    clock = Clock(dut.clk, 25, units="ns")
    cocotb.fork(clock.start())
    
    dut.RSTB.value = 0
    dut.power1.value = 0;
    dut.power2.value = 0;
    dut.power3.value = 0;
    dut.power4.value = 0;

    await ClockCycles(dut.clk, 8)
    dut.power1.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power2.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power3.value = 1;
    await ClockCycles(dut.clk, 8)
    dut.power4.value = 1;

    await ClockCycles(dut.clk, 80)
    dut.RSTB.value = 1

    # wait with a timeout for the project to become active
    await with_timeout(RisingEdge(dut.sync), 600, 'us')

    # wait
    await ClockCycles(dut.clk, 6000)

    # assert something
#    assert(0 == 25)

clocks_per_phase = 10


    # wait for the project to become active
   # await with_timeout(RisingEdge(dut.sync), 500, 'us')
#    await with_timeout(RisingEdge(dut.uut.mprj.PrimitiveCalculator.rst), 500, 'us')

async def run_encoder_test(encoder, dut_enc, max_count):
    for i in range(clocks_per_phase * 2 * max_count):
        await encoder.update(1)

    # let noisy transition finish, otherwise can get an extra count
    for i in range(10):
        await encoder.update(0)
    
    # when we have the internal signals (not GL) can also assert the values
    if dut_enc is not None:
        assert(dut_enc == max_count)

@cocotb.test()
async def test_all(dut):
    clock = Clock(dut.clk, 5, units="us")
    clocks_per_phase = 5
    # no noise
    encoder = Encoder_calc(dut.clk, dut.rotary_a, dut.rotary_b, clocks_per_phase = clocks_per_phase, noise_cycles = 0)
    cocotb.fork(clock.start())
    
    assert dut.seven_segment_out.value == 63
    
#    random_a = random.randint(0,255)
#    random_b = random.randint(0,255)

    random_a = 21
    random_b = 12
    
    # Start State
    dut.select.value = 1
    await ClockCycles(dut.clk, 10)
    dut.select.value = 0
    await ClockCycles(dut.clk, 3)
    
    # First Input State
    for i in range (clocks_per_phase * 2 * random_a):
        await encoder.update(1)

    dut.select.value = 1
    await ClockCycles(dut.clk, 10)
    dut.select.value = 0
    await ClockCycles(dut.clk, 3)        
    
#    await ClockCycles(dut.clk, 100)
    # Second Input State
    for i in range (random_a - random_b):
        await encoder.update(-1)

    dut.select.value = 1
    await ClockCycles(dut.clk, 10)
    dut.select.value = 0
    await ClockCycles(dut.clk, 3)  
    
    # Selection State for addition
    for i in range (12):
        await encoder.update(-1)

    dut.select.value = 1
    await ClockCycles(dut.clk, 10)
    dut.select.value = 0
    await ClockCycles(dut.clk, 3)  
    
    # Final State
    await ClockCycles(dut.clk, 3)
    if (dut.seven_segment_digit.value == 0):
        assert (dut.seven_segment_out.value == 6)
    else: 
        assert (dut.seven_segment_out.value == 91)
        
