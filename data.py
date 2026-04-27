# data.py

MUSCLE_DATA = {
    "💪 Biceps": {
        "color": "#ef4444",
        "exercises": [
            {"name": "Dumbbell Curl", "sets": "3×12", "tip": "Elbow fixed रखो, shoulder नहीं हिलाओ"},
            {"name": "Barbell Curl", "sets": "4×10", "tip": "Back straight, controlled movement"},
            {"name": "Hammer Curl", "sets": "3×12", "tip": "Neutral grip, brachialis target"},
            {"name": "Preacher Curl", "sets": "3×10", "tip": "Full extension लो, slow negative"},
            {"name": "Concentration Curl", "sets": "3×15", "tip": "Mind-muscle connection पर focus"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+biceps+workout+hindi",
        "info": "💡 Biceps = Arm का front muscle. Peak बनाने के लिए Preacher Curl best है।"
    },

    "🦾 Triceps": {
        "color": "#f97316",
        "exercises": [
            {"name": "Tricep Pushdown", "sets": "4×12", "tip": "Elbows body से touch रहें"},
            {"name": "Overhead Extension", "sets": "3×12", "tip": "Core tight, elbow flare मत करो"},
            {"name": "Skull Crushers", "sets": "3×10", "tip": "Weight को control करो"},
            {"name": "Close Grip Bench", "sets": "3×10", "tip": "Grip shoulder-width रखो"},
            {"name": "Tricep Dips", "sets": "3×15", "tip": "Chest को forward lean मत करो"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+triceps+workout+hindi",
        "info": "💡 Triceps = Arm का 2/3 हिस्सा! Arms बड़े करने हैं तो Triceps पर ज्यादा focus करो।"
    },

    "🏔️ Shoulder": {
        "color": "#eab308",
        "exercises": [
            {"name": "Overhead Press", "sets": "4×10", "tip": "Core brace, knees slightly bent"},
            {"name": "Lateral Raise", "sets": "3×15", "tip": "Slow & controlled, elbow slight bend"},
            {"name": "Front Raise", "sets": "3×12", "tip": "Don't use momentum"},
            {"name": "Arnold Press", "sets": "3×12", "tip": "Full rotation of wrist"},
            {"name": "Rear Delt Fly", "sets": "3×15", "tip": "Bend forward 45°, elbow wide"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+shoulder+workout+hindi",
        "info": "💡 3D Shoulders चाहिए? तीनों heads train करो।"
    },

    "🫁 Chest": {
        "color": "#ec4899",
        "exercises": [
            {"name": "Flat Bench Press", "sets": "4×10", "tip": "Arch back slightly, feet flat"},
            {"name": "Incline Dumbbell Press", "sets": "3×12", "tip": "Upper chest के लिए best"},
            {"name": "Cable Flyes", "sets": "3×15", "tip": "Full stretch at bottom"},
            {"name": "Push-Ups", "sets": "3×20", "tip": "Elbows 45°, chest to floor"},
            {"name": "Decline Press", "sets": "3×12", "tip": "Lower chest target"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+chest+workout+hindi",
        "info": "💡 Big Chest = Compound + Isolation combo।"
    },

    "🦵 Legs": {
        "color": "#22c55e",
        "exercises": [
            {"name": "Squats", "sets": "4×12", "tip": "Knees over toes, deep squat लो"},
            {"name": "Leg Press", "sets": "4×15", "tip": "Full depth, knees don't cave in"},
            {"name": "Romanian Deadlift", "sets": "3×12", "tip": "Hamstring stretch feel करो"},
            {"name": "Leg Extension", "sets": "3×15", "tip": "Quad squeeze at top"},
            {"name": "Calf Raises", "sets": "4×20", "tip": "Slow negatives, full range"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+leg+workout+hindi",
        "info": "💡 Leg day skip मत करो!"
    },

    "🏛️ Back": {
        "color": "#3b82f6",
        "exercises": [
            {"name": "Deadlift", "sets": "4×6", "tip": "Back flat, hinge at hips"},
            {"name": "Pull-Ups", "sets": "3×10", "tip": "Full extension, chin over bar"},
            {"name": "Barbell Row", "sets": "4×10", "tip": "Elbows back, squeeze lats"},
            {"name": "Lat Pulldown", "sets": "3×12", "tip": "Chest up, lean back slightly"},
            {"name": "Seated Cable Row", "sets": "3×15", "tip": "Shoulder blades squeeze"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+back+workout+hindi",
        "info": "💡 V-taper = Pull + Row combo।"
    },

    "🏃 Cardio": {
        "color": "#a855f7",
        "exercises": [
            {"name": "Treadmill Run", "sets": "20 min", "tip": "Incline add करो"},
            {"name": "Jump Rope", "sets": "5×3 min", "tip": "Wrist से jump करो"},
            {"name": "Cycling", "sets": "30 min", "tip": "Medium resistance"},
            {"name": "HIIT Intervals", "sets": "20 min", "tip": "30s max, 30s rest"},
            {"name": "Stair Climber", "sets": "15 min", "tip": "Don't hold rails"},
        ],
        "video": "https://www.youtube.com/results?search_query=best+cardio+fat+loss+hindi",
        "info": "💡 Fat loss = HIIT best।"
    },

    "🧘 Yoga": {
        "color": "#06b6d4",
        "exercises": [
            {"name": "Sun Salutation", "sets": "5 rounds", "tip": "Slow breathing"},
            {"name": "Warrior Pose", "sets": "Hold 30s", "tip": "Hip alignment"},
            {"name": "Downward Dog", "sets": "Hold 1 min", "tip": "Heels push down"},
            {"name": "Child's Pose", "sets": "Hold 2 min", "tip": "Relax"},
            {"name": "Shavasana", "sets": "5 min", "tip": "Complete rest"},
        ],
        "video": "https://www.youtube.com/results?search_query=yoga+for+beginners+hindi",
        "info": "💡 Yoga = Recovery + Mind।"
    },
}
