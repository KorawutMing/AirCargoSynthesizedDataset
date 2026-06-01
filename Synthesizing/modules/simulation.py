# simulation.py
import numpy as np
from config import MAX_SHIPMENT_SIZE_KG, SEGMENT_ELASTICITY

def rm_decision_model(request, flight_state):
    """
    Determines whether to accept or reject a booking request.
    Implements dual-constraint physical capacity logic (Weight & Volume).
    """
    # Physical constraint check: Weight
    if flight_state['remaining_capacity_kg'] < request['weight']:
        return False, "Weight Capacity Exceeded"
        
    # Physical constraint check: Volume
    if flight_state['remaining_capacity_cbm'] < request['volume']:
        return False, "Volume Capacity Exceeded"
        
    return True, "Accepted"

def simulate_flight_booking_window(flight_id, total_capacity_kg, total_capacity_cbm, base_demand, 
                                   temporal_mult, price_matrix, price_index,
                                   booking_curves, segments_config):
    """
    Simulates the 15-day discrete transaction queue for a single flight.
    """
    flight_state = {
        'total_capacity_kg': total_capacity_kg,
        'remaining_capacity_kg': total_capacity_kg,
        'total_capacity_cbm': total_capacity_cbm,
        'remaining_capacity_cbm': total_capacity_cbm,
        'd_close': 0, # DP when capacity hit 0
        'is_censored': False,
        'censored_by': None
    }

    realized_log = [] 
    latent_log = []   

    # Iterate chronologically from DP=-15 to DP=-1
    for dp in sorted(booking_curves.index):

        daily_requests = []

        # The theoretical mean of a lognormal(5.0, 1.0) is exp(5.0 + 0.5) ≈ 244.7 kg
        AVG_SHIPMENT_WEIGHT = 245.0 

        for segment, params in segments_config.items():
            arrival_pct = booking_curves.loc[dp, segment]
            price = price_matrix[segment][dp]
            density = params['density']

            elasticity = SEGMENT_ELASTICITY.get(segment, 1.0)
            elasticity_factor = price_index ** (-elasticity)

            expected_demand_kg = base_demand * temporal_mult * params['weight'] * arrival_pct * elasticity_factor
            lam = expected_demand_kg / AVG_SHIPMENT_WEIGHT

            num_requests = np.random.poisson(lam)

            if num_requests > 0:
                weights = np.random.lognormal(mean=5.0, sigma=1.0, size=num_requests)
                weights = np.clip(weights, 10, MAX_SHIPMENT_SIZE_KG) 

                for w in weights:
                    daily_requests.append({
                        'flight_id': flight_id,
                        'segment': segment,
                        'dp': dp,
                        'weight': round(w, 2),
                        'volume': round(w / density, 2),
                        'price': price
                    })

        np.random.shuffle(daily_requests)

        for req in daily_requests:
            latent_log.append(req)

            accepted, reason = rm_decision_model(req, flight_state)

            if accepted:
                flight_state['remaining_capacity_kg'] -= req['weight']
                flight_state['remaining_capacity_cbm'] -= req['volume']
                realized_log.append(req)
            else:
                if not flight_state['is_censored']:
                    flight_state['is_censored'] = True
                    flight_state['d_close'] = dp
                    flight_state['censored_by'] = "Weight" if "Weight" in reason else "Volume"

    return flight_state, realized_log, latent_log