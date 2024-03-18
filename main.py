import pyromat as pm
h20 = pm.get('mp.H2O')
r134a = pm.get('mp.C2H2F4')


def get_cooling_tower_temperature(wet_bulb_temperature, temperature_reduction):
    Twb = wet_bulb_temperature
    Tr = temperature_reduction
    a = 16.790751
    b = 0.6464308
    c = 2.2221763
    d = 0.0016061
    e = -0.0159268
    f = -0.015954
    return a + b*Twb + c*Tr + d*Twb**2 + e*Tr**2 + f*Tr*Twb


def model_chiller(
        fluid,
        wet_bulb_temperature=70.0,
        primary_supply_temperature=40.0,
        condenser_temperature_difference=10.0,
        evaporator_temperature_difference=10.0,
        volume_flow_rate=3.0
):
    # Set the units
    pm.config['unit_temperature'] = 'F'

    # Calculate the mass flow rate
    volume_flow_rate *= 6.309e-5        # gal / min to m^3 / s
    mass_flow_rate = fluid.d() * volume_flow_rate
    print(fluid.d())
    print(mass_flow_rate)


    # Get the cooling tower temperature
    cooling_tower_temperature = get_cooling_tower_temperature(wet_bulb_temperature, condenser_temperature_difference)

    # Get the temperatures within the chiller
    T1 = primary_supply_temperature - evaporator_temperature_difference
    T3 = cooling_tower_temperature + condenser_temperature_difference

    # Get the state info
    state_1 = fluid.state(x=1, T=T1)                            # Before the compressor
    state_3 = fluid.state(x=0, T=T3)                            # Before the condenser
    state_2 = fluid.state(p=state_3['p'], s=state_1['s'])       # Before the expansion
    state_4 = fluid.state(p=state_1['p'], s=state_3['s'])       # Before the evaporator

    print(fluid.d(p=state_1['p']))
    print(fluid.d(p=state_3['p']))

    # Calculate the work
    work = mass_flow_rate * (state_1['h'] - state_4['h'])
    print(work)


def main():
    model_chiller(fluid=r134a)


if __name__ == '__main__':
    main()
