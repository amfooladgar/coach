# agents/scheduler.py
import uuid
import datetime
from datetime import datetime as dt, timedelta
from typing import List, Tuple
from data.schemas import Task, CalendarEvent


def _parse_time(time_str: str, date: datetime.date = None) -> dt:
    """Parse time string (HH:MM) into datetime object."""
    if date is None:
        date = datetime.date.today()
    hour, minute = map(int, time_str.split(":"))
    return dt.combine(date, datetime.time(hour, minute))


def _parse_time_range(time_range: str, date: datetime.date = None) -> Tuple[dt, dt]:
    """Parse time range string (HH:MM-HH:MM) into start and end datetime."""
    start_str, end_str = time_range.split("-")
    return _parse_time(start_str.strip(), date), _parse_time(end_str.strip(), date)


def _get_fixed_blocks(config: dict, date: datetime.date = None) -> List[Tuple[dt, dt, str]]:
    """
    Extract fixed time blocks from config (gym, sleep, breaks).
    Returns list of (start_time, end_time, label) tuples.
    """
    if date is None:
        date = datetime.date.today()
    
    fixed_blocks = []
    user_cfg = config.get("user", {})
    
    # Gym time
    gym_time = user_cfg.get("gym_time")
    if gym_time:
        gym_start = _parse_time(gym_time, date)
        gym_end = gym_start + timedelta(hours=1)  # Assume 1-hour gym session
        fixed_blocks.append((gym_start, gym_end, "🏋️ Gym"))
    
    # Evening reflection block (from schedule config)
    evening_reflect = config.get("schedule", {}).get("evening_reflect")
    if evening_reflect:
        reflect_start = _parse_time(evening_reflect, date)
        reflect_end = reflect_start + timedelta(minutes=30)
        fixed_blocks.append((reflect_start, reflect_end, "📝 Evening Reflection"))
    
    return fixed_blocks


def _is_time_available(start: dt, end: dt, fixed_blocks: List[Tuple[dt, dt, str]]) -> bool:
    """Check if a time slot conflicts with any fixed blocks."""
    for block_start, block_end, _ in fixed_blocks:
        # Check for overlap
        if not (end <= block_start or start >= block_end):
            return False
    return True


def _get_preferred_work_blocks(config: dict, date: datetime.date = None) -> List[Tuple[dt, dt]]:
    """Extract preferred work blocks from config."""
    if date is None:
        date = datetime.date.today()
    
    user_cfg = config.get("user", {})
    work_blocks_str = user_cfg.get("preferred_work_blocks", [])
    
    work_blocks = []
    for block in work_blocks_str:
        start, end = _parse_time_range(block, date)
        work_blocks.append((start, end))
    
    return work_blocks


def schedule_tasks(tasks: List[Task], config: dict) -> List[CalendarEvent]:
    """
    Map tasks to calendar time blocks respecting constraints.
    
    Algorithm:
    1. Parse config constraints (wake time, gym, work blocks)
    2. Create timeline of available slots
    3. Sort tasks by priority and energy
    4. Assign deep work to morning, light work to afternoon
    5. Generate CalendarEvent objects
    
    Args:
        tasks: List of Task objects from planner
        config: User config with wake_time, gym_time, work_blocks, etc.
    
    Returns:
        List of CalendarEvent objects with scheduled time blocks
    """
    if not tasks:
        return []
    
    user_cfg = config.get("user", {})
    scheduler_cfg = config.get("agents", {}).get("scheduler", {})
    
    # Get today's date
    today = datetime.date.today()
    
    # Parse wake time and end-of-day
    wake_time_str = user_cfg.get("wake_time", "08:00")
    wake_time = _parse_time(wake_time_str, today)
    
    # End scheduling before evening reflection (default 21:00)
    evening_reflect = config.get("schedule", {}).get("evening_reflect", "21:00")
    day_end = _parse_time(evening_reflect, today)
    
    # Get fixed blocks (gym, reflection, etc.)
    fixed_blocks = _get_fixed_blocks(config, today)
    
    # Get preferred work blocks
    work_blocks = _get_preferred_work_blocks(config, today)
    
    # Sort tasks by priority (P1 > P2 > P3) and energy (deep > steady > light)
    priority_order = {"P1": 1, "P2": 2, "P3": 3}
    energy_order = {"deep": 1, "steady": 2, "light": 3}
    
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (priority_order.get(t.priority, 3), energy_order.get(t.energy, 2))
    )
    
    # Generate scheduled events
    events: List[CalendarEvent] = []
    current_time = wake_time
    
    # Add fixed blocks first (for display purposes)
    for block_start, block_end, label in fixed_blocks:
        events.append(CalendarEvent(
            event_id=str(uuid.uuid4()),
            task_id=None,
            title=label,
            start_time=block_start,
            end_time=block_end,
            duration_min=int((block_end - block_start).total_seconds() / 60),
            block_type="fixed",
            created_at=dt.now()
        ))
    
    # Schedule tasks
    for task in sorted_tasks:
        duration = timedelta(minutes=task.duration_est_min)
        buffer = timedelta(minutes=10)  # Buffer between tasks
        
        # For deep work, prefer morning work blocks if configured
        prefer_morning = (
            scheduler_cfg.get("deep_work_morning", True) and 
            task.energy == "deep"
        )
        
        # Try to find a suitable time slot
        scheduled = False
        search_start = current_time
        
        # If prefer morning and we have work blocks, try those first
        if prefer_morning and work_blocks:
            for work_start, work_end in work_blocks:
                if work_start < dt.combine(today, datetime.time(12, 0)):  # Morning blocks
                    # Try to fit task in this work block
                    slot_start = max(search_start, work_start)
                    slot_end = slot_start + duration
                    
                    if slot_end <= work_end and _is_time_available(slot_start, slot_end, fixed_blocks):
                        # Found a good slot
                        events.append(CalendarEvent(
                            event_id=str(uuid.uuid4()),
                            task_id=task.task_id,
                            title=f"[{task.priority}] {task.title}",
                            start_time=slot_start,
                            end_time=slot_end,
                            duration_min=task.duration_est_min,
                            block_type="work",
                            created_at=dt.now()
                        ))
                        current_time = slot_end + buffer
                        scheduled = True
                        break
        
        # If not scheduled yet, find next available slot
        if not scheduled:
            while current_time + duration <= day_end:
                slot_end = current_time + duration
                
                if _is_time_available(current_time, slot_end, fixed_blocks):
                    # Found an available slot
                    events.append(CalendarEvent(
                        event_id=str(uuid.uuid4()),
                        task_id=task.task_id,
                        title=f"[{task.priority}] {task.title}",
                        start_time=current_time,
                        end_time=slot_end,
                        duration_min=task.duration_est_min,
                        block_type="work",
                        created_at=dt.now()
                    ))
                    current_time = slot_end + buffer
                    scheduled = True
                    break
                else:
                    # Skip past the blocking fixed event
                    for block_start, block_end, _ in fixed_blocks:
                        if block_start <= current_time < block_end:
                            current_time = block_end + buffer
                            break
                    else:
                        # No blocking event found, just increment by 15 min
                        current_time += timedelta(minutes=15)
        
        if not scheduled:
            # Task couldn't be scheduled - add to end of day or skip
            # For now, let's add it unscheduled with a warning
            print(f"⚠️ Warning: Could not schedule task '{task.title}' - no available time slots")
    
    # Sort all events by start time for clean display
    events.sort(key=lambda e: e.start_time)
    
    return events
