import tkinter as tk
from tkinter import ttk

def exosight_ai_explorer_gui():
    """
    A GUI for the ExoSight AI Explorer using tkinter.
    """
    exoplanet_data = {
        "TRAPPIST-1d": {
            "system": "TRAPPIST-1",
            "discovery_mission": "TRAPPIST",
            "planet_type": "Rocky, Earth-sized",
            "fun_fact": "One of seven rocky worlds in its system; its atmosphere is a key target for JWST.",
        },
        "Kepler-186f": {
            "system": "Kepler-186",
            "discovery_mission": "Kepler",
            "planet_type": "Terrestrial",
            "fun_fact": "The first rocky planet discovered within the habitable zone of another star.",
        },
        "51 Pegasi b": {
            "system": "51 Pegasi",
            "discovery_mission": "Observatoire de Haute-Provence",
            "planet_type": "Gas Giant (Hot Jupiter)",
            "fun_fact": "The first exoplanet discovered orbiting a sun-like star, awarded the 2019 Nobel Prize in Physics.",
        },
        "TOI 700 d": {
            "system": "TOI 700",
            "discovery_mission": "TESS",
            "planet_type": "Earth-sized",
            "fun_fact": "The first Earth-sized planet discovered by TESS in its star's habitable zone.",
        },
        "Wolf 503b": {
            "system": "Wolf 503",
            "discovery_mission": "Kepler",
            "planet_type": "Super-Earth",
            "fun_fact": "Twice the size of Earth, it is significant for its size, which falls into a rarely observed category known as the 'Fulton gap'.",
        },
         "TRAPPIST-1e": {
            "system": "TRAPPIST-1",
            "discovery_mission": "TRAPPIST",
            "planet_type": "Rocky, Earth-sized",
            "fun_fact": "Considered one of the most promising of the TRAPPIST-1 planets for habitability.",
        },
        "Kepler-452b": {
            "system": "Kepler-452",
            "discovery_mission": "Kepler",
            "planet_type": "Super-Earth",
            "fun_fact": "Sometimes nicknamed 'Earth's cousin' due to its similar orbit around a Sun-like star.",
        },
    }

    # --- UI Functions ---
    def on_planet_select(event):
        selected_indices = planet_listbox.curselection()
        if not selected_indices:
            return
        selected_planet_name = planet_listbox.get(selected_indices[0])
        planet_info = exoplanet_data.get(selected_planet_name)

        if planet_info:
            details_text = (
                f"System: {planet_info['system']}\n\n"
                f"Discovery Mission: {planet_info['discovery_mission']}\n\n"
                f"Planet Type: {planet_info['planet_type']}\n\n"
                f"Fun Fact: {planet_info['fun_fact']}"
            )
            details_content.config(state=tk.NORMAL)
            details_content.delete("1.0", tk.END)
            details_content.insert(tk.END, details_text)
            details_content.config(state=tk.DISABLED)
            title_label.config(text=selected_planet_name)

    def populate_planet_list(filter_mission=None):
        planet_listbox.delete(0, tk.END)
        if filter_mission and filter_mission != "All":
            planets_to_show = [
                name for name, details in exoplanet_data.items()
                if details['discovery_mission'].lower() == filter_mission.lower()
            ]
        else:
            planets_to_show = exoplanet_data.keys()

        for planet in sorted(planets_to_show):
            planet_listbox.insert(tk.END, planet)

    # --- Create the Main Window ---
    root = tk.Tk()
    root.title("ExoSight AI Explorer")
    root.geometry("800x600")
    root.configure(bg="#1e1e1e")

    # --- Main Frames ---
    left_frame = tk.Frame(root, width=300, bg="#2a2a2a", padx=10, pady=10)
    left_frame.pack(side="left", fill="y")
    left_frame.pack_propagate(False)

    right_frame = tk.Frame(root, bg="#1e1e1e", padx=20, pady=20)
    right_frame.pack(side="right", fill="both", expand=True)

    # --- Left Panel: Filters and Planet List ---
    filter_label = tk.Label(left_frame, text="Filter by Mission", fg="white", bg="#2a2a2a", font=("Helvetica", 12, "bold"))
    filter_label.pack(pady=(0, 10))

    filter_frame = tk.Frame(left_frame, bg="#2a2a2a")
    filter_frame.pack(fill="x", pady=5)
    
    missions = ["All", "Kepler", "TESS", "TRAPPIST"]
    for mission in missions:
        btn = ttk.Button(filter_frame, text=mission, command=lambda m=mission: populate_planet_list(m))
        btn.pack(side="left", fill="x", expand=True, padx=2)

    list_label = tk.Label(left_frame, text="Exoplanets", fg="white", bg="#2a2a2a", font=("Helvetica", 12, "bold"))
    list_label.pack(pady=(20, 10))
    
    planet_listbox = tk.Listbox(left_frame, bg="#3c3c3c", fg="white", selectbackground="#5c5c5c", borderwidth=0, highlightthickness=0, font=("Helvetica", 11))
    planet_listbox.pack(fill="both", expand=True)
    planet_listbox.bind("<<ListboxSelect>>", on_planet_select)

    # --- Right Panel: Planet Details ---
    title_label = tk.Label(right_frame, text="Select an Exoplanet", fg="#00aaff", bg="#1e1e1e", font=("Helvetica", 24, "bold"))
    title_label.pack(pady=(0, 20), anchor="w")

    details_content = tk.Text(right_frame, bg="#1e1e1e", fg="white", wrap=tk.WORD, borderwidth=0, highlightthickness=0, font=("Helvetica", 14), spacing3=10)
    details_content.pack(fill="both", expand=True)
    details_content.insert(tk.END, "Welcome to the ExoSight AI Explorer!\n\nSelect a planet from the list on the left to see its details.")
    details_content.config(state=tk.DISABLED)

    # --- Initial Population ---
    populate_planet_list("All")

    # --- Start the UI Loop ---
    root.mainloop()

if __name__ == "__main__":
    exosight_ai_explorer_gui()