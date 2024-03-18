import pyromat as pm
h20 = pm.get('mp.H2O')
r134a = pm.get('mp.C2H2F4')


def get_cooling_tower_return_temperature(wet_bulb_temperature, temperature_reduction):
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
        wet_bulb_temperature=70.0,              # Twb
        primary_supply_temperature=40.0,        # Tch
        condenser_temperature_reduction=10.0,   # todo: verify this
        chilled_water_temperature_drop=10.0,
        chiller_tons=1.0,
        cooling_tower_flow_rate_gpm=3.0,
        evaporator_effectiveness=0.8,
        condenser_effectiveness=0.8
):
    # Set the units
    pm.config['unit_temperature'] = 'F'
    print(pm.config)

    # Get the Q from the evaporator (this is our design point)
    Qin = chiller_tons * 3.5168528421                                   # kW

    # Get the chilled water temperatures
    Tch_out = primary_supply_temperature
    Tch_in = Tch_out + chilled_water_temperature_drop

    # Calculate the mass flow rate of the chilled water
    Tch_avg = 0.5 * (Tch_out + Tch_in)
    m_ch = Qin / (h20.cp(T=Tch_avg) * (Tch_in - Tch_out))               # kg/s

    # Let's assume Cmin = mcp_ch (todo: verify this)
    c_min_evap = m_ch * h20.cp(T=Tch_avg)

    # Calculate T4 based on the effectiveness of the evaporator
    T4 = Tch_in - Qin / evaporator_effectiveness / c_min_evap

    # Get the cooling tower temperatures
    Tct_in = get_cooling_tower_return_temperature(wet_bulb_temperature, condenser_temperature_reduction)
    Tct_out = Tct_in + condenser_temperature_reduction

    # Convert cooling tower flow rate to a mass flow rate
    Tct_avg = 0.5 * (Tct_in + Tct_out)
    m_ct = cooling_tower_flow_rate_gpm * h20.d(T=Tct_avg) * 6.309e-5    # kg/s

    # Calculate Qout
    Qout = m_ct * h20.cp(T=Tct_avg) * (Tct_out - Tct_in)                # kW

    # Let's assume Cmin = mcp_ct (todo: verify this)
    c_min_cond = m_ct * h20.cp(T=Tct_avg)

    # Calculate T2 based on the effectiveness of the condenser
    T2 = Tct_in + Qout / condenser_effectiveness / c_min_cond

    # Get the state info
    state_1 = fluid.state(x=1, T=T4)                            # We're assuming T1=T4
    state_2 = fluid.state(T=T2, s=state_1['s'])                 # I'm assuming s2=s1 todo: verify this
    state_3 = fluid.state(x=0, p=state_2['p'])                  # We're assuming p3=p2
    state_4 = fluid.state(T=T4, h=state_3['h'])                 # We're assuming h4=h3 todo: verify this

    # Calculate the chiller mass flow rate
    chiller_mass_flow_rate = Qin / (state_1['h'] - state_4['h'])

    # Calculate the work
    chiller_work = chiller_mass_flow_rate * (state_2['h'] - state_1['h'])
    print(chiller_work)


def main():
    model_chiller(fluid=r134a)


if __name__ == '__main__':
    main()
