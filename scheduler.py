def has_conflict(new_event, events):
    for e in events:
        if e["Date"] == new_event["Date"]:
            if new_event["Start Time"] < e["End Time"] and new_event["End Time"] > e["Start Time"]:
                return True
    return False

def find_free_slots(events, date):
    from datetime import time
    
    day_events = [e for e in events if str(e["Date"]) == str(date)]
    day_events.sort(key=lambda x: x["Start Time"])
    
    free_slots = []
    day_start = time(8, 0)
    day_end = time(20, 0)
    
    if not day_events:
        free_slots.append(f"8:00 AM - 8:00 PM (Full day free)")
        return free_slots
    
    # Before first event
    if day_events[0]["Start Time"] > day_start:
        free_slots.append(f"{day_start.strftime('%I:%M %p')} - {day_events[0]['Start Time'].strftime('%I:%M %p')}")
    
    # Between events
    for i in range(len(day_events) - 1):
        end = day_events[i]["End Time"]
        next_start = day_events[i+1]["Start Time"]
        if end < next_start:
            free_slots.append(f"{end.strftime('%I:%M %p')} - {next_start.strftime('%I:%M %p')}")
    
    # After last event
    if day_events[-1]["End Time"] < day_end:
        free_slots.append(f"{day_events[-1]['End Time'].strftime('%I:%M %p')} - {day_end.strftime('%I:%M %p')}")
    
    return free_slots if free_slots else ["No free slots today"]