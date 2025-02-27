from datetime import datetime, timedelta
import pytz
import pandas as pd
from kpTools.VedicAstro import VedicHoroscopeData
from tabulate import tabulate


def get_position_data(chart_data, time):
    """Get Moon and Ascendant position data at a specific time"""
    # Generate chart
    chart = chart_data.generate_chart()

    # Get planetary positions
    planets_data = chart_data.get_planets_data_from_chart(chart)

    # Find Moon and Ascendant data
    moon_data = None
    asc_data = None

    for planet in planets_data:
        if planet.Object == "Moon":
            moon_data = planet
        elif planet.Object == "Asc":
            asc_data = planet

    return {
        'moon': {
            'position': moon_data.LonDecDeg,
            'rashi': moon_data.Rasi,
            'nakshatra': moon_data.Nakshatra,
            'rashi_lord': moon_data.RasiLord,
            'nakshatra_lord': moon_data.NakshatraLord,
            'sub_lord': moon_data.SubLord,
            'sub_sub_lord': moon_data.SubSubLord
        },
        'ascendant': {
            'position': asc_data.LonDecDeg,
            'rashi': asc_data.Rasi,
            'nakshatra': asc_data.Nakshatra,
            'rashi_lord': asc_data.RasiLord,
            'nakshatra_lord': asc_data.NakshatraLord,
            'sub_lord': asc_data.SubLord,
            'sub_sub_lord': asc_data.SubSubLord
        }
    }


def position_changed(pos1, pos2, body_type):
    """Check if any relevant parameter changed between two positions"""
    if pos1 is None or pos2 is None:
        return True

    return (
            pos1[body_type]['rashi'] != pos2[body_type]['rashi'] or
            pos1[body_type]['nakshatra'] != pos2[body_type]['nakshatra'] or
            pos1[body_type]['rashi_lord'] != pos2[body_type]['rashi_lord'] or
            pos1[body_type]['nakshatra_lord'] != pos2[body_type]['nakshatra_lord'] or
            pos1[body_type]['sub_lord'] != pos2[body_type]['sub_lord'] or
            pos1[body_type]['sub_sub_lord'] != pos2[body_type]['sub_sub_lord']
    )


def main():
    # Mumbai coordinates
    latitude = 19.0760
    longitude = 72.8777
    utc_offset = "+5:30"

    # Current date and time in Mumbai
    mumbai_tz = pytz.timezone('Asia/Kolkata')
    start_time = datetime.now(mumbai_tz)
    end_time = start_time + timedelta(hours=1)

    print(
        f"\nAnalyzing positions from {start_time.strftime('%Y-%m-%d %H:%M:%S')} to {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Mumbai time)")

    # Initialize data collection
    moon_transitions = []
    asc_transitions = []

    # Initialize with starting time
    current_time = start_time
    step_minutes = 1  # Check every minute

    # Get initial position
    chart_data = VedicHoroscopeData(
        year=current_time.year,
        month=current_time.month,
        day=current_time.day,
        hour=current_time.hour,
        minute=current_time.minute,
        second=current_time.second,
        utc=utc_offset,
        latitude=latitude,
        longitude=longitude,
        ayanamsa="Krishnamurti",
        house_system="Placidus"
    )

    last_position = get_position_data(chart_data, current_time)

    moon_start_time = current_time
    asc_start_time = current_time

    # Track changes over 1 hour
    while current_time <= end_time:
        # Move to next time step
        current_time += timedelta(minutes=step_minutes)

        # Create chart data for current time
        chart_data = VedicHoroscopeData(
            year=current_time.year,
            month=current_time.month,
            day=current_time.day,
            hour=current_time.hour,
            minute=current_time.minute,
            second=current_time.second,
            utc=utc_offset,
            latitude=latitude,
            longitude=longitude,
            ayanamsa="Krishnamurti",
            house_system="Placidus"
        )

        # Get current position
        current_position = get_position_data(chart_data, current_time)

        # Check for Moon transitions
        if position_changed(last_position, current_position, 'moon'):
            # Add the last period that just ended
            moon_transitions.append({
                'start_time': moon_start_time,
                'end_time': current_time,
                'position': last_position['moon']['position'],
                'rashi': last_position['moon']['rashi'],
                'nakshatra': last_position['moon']['nakshatra'],
                'rashi_lord': last_position['moon']['rashi_lord'],
                'nakshatra_lord': last_position['moon']['nakshatra_lord'],
                'sub_lord': last_position['moon']['sub_lord'],
                'sub_sub_lord': last_position['moon']['sub_sub_lord']
            })
            # Reset start time for new period
            moon_start_time = current_time

        # Check for Ascendant transitions
        if position_changed(last_position, current_position, 'ascendant'):
            # Add the last period that just ended
            asc_transitions.append({
                'start_time': asc_start_time,
                'end_time': current_time,
                'position': last_position['ascendant']['position'],
                'rashi': last_position['ascendant']['rashi'],
                'nakshatra': last_position['ascendant']['nakshatra'],
                'rashi_lord': last_position['ascendant']['rashi_lord'],
                'nakshatra_lord': last_position['ascendant']['nakshatra_lord'],
                'sub_lord': last_position['ascendant']['sub_lord'],
                'sub_sub_lord': last_position['ascendant']['sub_sub_lord']
            })
            # Reset start time for new period
            asc_start_time = current_time

        # Update last position
        last_position = current_position

    # Add final entries if we haven't reached a transition by end_time
    if moon_start_time < end_time:
        moon_transitions.append({
            'start_time': moon_start_time,
            'end_time': end_time,
            'position': last_position['moon']['position'],
            'rashi': last_position['moon']['rashi'],
            'nakshatra': last_position['moon']['nakshatra'],
            'rashi_lord': last_position['moon']['rashi_lord'],
            'nakshatra_lord': last_position['moon']['nakshatra_lord'],
            'sub_lord': last_position['moon']['sub_lord'],
            'sub_sub_lord': last_position['moon']['sub_sub_lord']
        })

    if asc_start_time < end_time:
        asc_transitions.append({
            'start_time': asc_start_time,
            'end_time': end_time,
            'position': last_position['ascendant']['position'],
            'rashi': last_position['ascendant']['rashi'],
            'nakshatra': last_position['ascendant']['nakshatra'],
            'rashi_lord': last_position['ascendant']['rashi_lord'],
            'nakshatra_lord': last_position['ascendant']['nakshatra_lord'],
            'sub_lord': last_position['ascendant']['sub_lord'],
            'sub_sub_lord': last_position['ascendant']['sub_sub_lord']
        })

    # Format and display results
    if moon_transitions:
        print("\n---------------- MOON TRANSITIONS ----------------")
        df_moon = pd.DataFrame(moon_transitions)
        # Format datetime columns
        df_moon['start_time'] = df_moon['start_time'].apply(lambda x: x.strftime('%H:%M:%S'))
        df_moon['end_time'] = df_moon['end_time'].apply(lambda x: x.strftime('%H:%M:%S'))
        print(tabulate(df_moon, headers='keys', tablefmt='grid', showindex=False))
    else:
        print("\nNo Moon transitions detected in the given time frame.")

    if asc_transitions:
        print("\n--------------- ASCENDANT TRANSITIONS ---------------")
        df_asc = pd.DataFrame(asc_transitions)
        # Format datetime columns
        df_asc['start_time'] = df_asc['start_time'].apply(lambda x: x.strftime('%H:%M:%S'))
        df_asc['end_time'] = df_asc['end_time'].apply(lambda x: x.strftime('%H:%M:%S'))
        print(tabulate(df_asc, headers='keys', tablefmt='grid', showindex=False))
    else:
        print("\nNo Ascendant transitions detected in the given time frame.")


if __name__ == "__main__":
    main()