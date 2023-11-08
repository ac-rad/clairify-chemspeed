import openai
import json
from match_function import match_to_function


functions = [
        {
            "name": "prime_pumps",
            "description": "Primes the ChemSpeed pumps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pump": {
                        "type": "string",
                        "description": "pump being primed",
                    },
                    "volume": {
                        "type": "string",
                        "description": "volume with which to prime pumps"},
                },
                "required": ["pump", "volume"],
            },
        },
        {
            "name": "transfer_liquid",
            "description": "Executes a liquid transfer from the source to the target zone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source zone for the liquid transfer."
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination zone for the liquid transfer."
                    },
                    "volume": {
                        "type": "number",
                        "description": "Volume to transfer [mL]"
                    },
                    "needle": {
                        "type": "integer",
                        "description": "Number of the needle to use (0 means all needles)."
                    },
                },
                "required": ["source", "destination", "volume", "needle"],
            },
        },
        {
            "name": "transfer_solid",
            "description": "Executes a solid transfer from the source to the target destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source zone for the solid transfer."
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination zone for the solid transfer."
                    },
                    "weight": {
                        "type": "number",
                        "description": "Mass to dispense [mg]"
                    },
                },
                "required": ["source", "destination", "weight"],
            },
        },
        {
            "name": "do_schlenk_cycles",
            "description": "Performs Schlenk Cycles (evacuate-refill cycles) on the specified wells.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wells": {
                        "type": "string",
                        "description": "Zones to be set to inert gas."
                    },
                    "evac_time": {
                        "type": "integer",
                        "description": "Time (in sec) for evacuation. Default: 60 sec."
                    },
                    "backfill_time": {
                        "type": "integer",
                        "description": "Time (in sec) for backfilling with inert gas. Default: 30 sec."
                    },
                },
                "required": ["wells"],
            },
        },
        {
            "name": "heat_under_reflux",
            "description": "Sets up the heating and the reflux condenser for a specified time period. Cools the system back to room temperature for a specified cooling period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wells": {
                        "type": "string",
                        "description": "wells to be heated under reflux."
                    },
                    "stir_rate": {
                        "type": "number",
                        "description": "Stir rate (in rpm)"
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Heating temperature (in °C)"
                    },
                    "heating_hours": {
                        "type": "integer",
                        "description": "Heating time (in h)"
                    },
                    "cooling_hours": {
                        "type": "integer",
                        "description": "Cooling time (in h)"
                    },
                    "condenser_temperature": {
                        "type": "number",
                        "description": "Temperature (in °C) of the reflux condenser."
                    },
                },
                "required": ["wells", "stir_rate", "temperature", "heating_hours", "cooling_hours"],
            },
        },
        {
            "name": "filter_liquid",
            "description": "Filters a liquid sample on a filtration rack. Allows for collecting the filtrate, washing and eluting the filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_well": {
                        "type": "string",
                        "description": "Source well of the sample to be filtered."
                    },
                    "filtration_zone": {
                        "type": "string",
                        "description": "Zone on the filtration rack to be used."
                    },
                    "filtration_volume": {
                        "type": "number",
                        "description": "Volume (in mL) of liquid to be filtered."
                    },
                },
                "required": ["source_well", "filtration_zone", "filtration_volume"],
            },
        },
    ]

def segment(prompt, socketio):
    prompt = f"Transform the following instructions into structured actions:\n\"{prompt}\".\n\nActions:\n"

    # Generate structured actions using OpenAI's GPT model
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2000,
        temperature=0,
        stop=None
    )
    actions = response.choices[0].text.strip().split("\n")
    socketio.emit("message", f"{actions}")
    return actions

def convert_action_to_function(action, functions, socketio):
    routine_functions = ["prime_pumps", "inject_to_hplc", "do_schlenk_cycles", "heat_under_reflux", "filter_liquid", "set_isynth_drawers"]
    messages = [{"role":"system", "content":"You are a natural language to Chemspeed translator, you must also do your best to correct any incorrect Chemspeed, only use items contained in the description. Convert to your best estimate even if not enough information is provided" },
                {"role": "user", "content": "Prime pump 1 with 30 mL using chemspd as manager."},
                {"role": "assistant", "content": "", "function_call": {'name': 'prime_pump', 'arguments': "{'pump': '1', 'volume': '30', 'manager': 'chemspd'}"}},
                # {"role": "user", "content": "Transfer 10 mL of liquid from the source zone to the destination zone using needle 1."},
                {"role": "user", "content": "Translate the following into Chemspeed syntax "+ action}]
    
    socketio.emit("message", f"Function matched: {match_to_function(action, functions)}")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call={"name": match_to_function(action, functions)},
        #temperature = 0,
        #top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=False,
    )
    response_message = json.loads(str(response["choices"][0]["message"]))
    socketio.emit("message", f"{response_message}, {type(response_message)}")

    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]
        function_args = json.loads(response_message["function_call"]["arguments"])
        print(function_args)
        arguments = []
        if function_name in routine_functions:
            function_code = f"routines.{function_name}("
            arguments.append("chmspd=chmspd")
        else:
            function_code = f"chemspd.{function_name}("
        for arg_name in function_args:
            arg_value = function_args[arg_name]
            if type(arg_value) is str:
                arg_value.replace('"', '')
            arguments.append(f"{arg_name}={arg_value}")
        function_code += ", ".join(arguments)
        function_code += ")"

        socketio.emit("message", function_code)
        socketio.emit("correct_structured", function_code)
    socketio.emit("message", response_message)

def convert(prompt, socketio):
    prompt_actions = segment(prompt, socketio)
    print(prompt_actions, type(prompt_actions), len(prompt_actions))
    for action in prompt_actions:
        convert_action_to_function(action, functions, socketio)
    
    
    

if __name__ == '__main__':
    procedure = [
        """Prime pump 1 with 30 mL using chemspd as manager.
Transfer 10 mL of THF (liquid) from thf to internal_standard with needle 1.
Transfer 0.1 mg of boronic acid (solid) from bmida to rxn_well.
Transfer 0.1 mg of halide (solid) from halide to rxn_well.
Transfer 0.1 mg of base (solid) from base to rxn_well.
Perform Schlenk cycles on rxn_well with 60 sec evacuation and 30 sec backfill_time.
Transfer 0.1 mL of catalyst solution from catalyst_solution to rxn_well with needle 1.
Transfer 1.0 mL of solvent from solvent to rxn_well with needle 1.
Transfer 1.0 mL of water from water to rxn_well with needle 4.
Reflux rxn_well at 100 rpm, 100 C, heat and cool 1 hour and condenser temperature at 20 C.
Transfer 10 mL of internal standard (liquid) from internal_standard to rxn_well with needle 1.
Filter 3 mL liquid sourced from rxn_well. Use filter_cartridge as filtration rack.
Transfer 3.0 mL of THF (liquid) from thf into filter_cartridge with needle 1.
Transfer 0.2 mL liquid from filtrate_well to hplc_port with needle 1.
"""
    ]
    for prompt in procedure:
        print(f"# {prompt}")
        convert(prompt)
        print()
# result:
"""
# Prime pump 1 with 30 mL using chemspd as manager
prime_pumps(chmspd=chmspd, pump=1, volume=30)

# Transfer 10 mL of THF (liquid) from thf to internal_standard with needle 1
transfer_liquid(chmspd=chmspd, source=thf, destination=internal_standard, volume=10, needle=1)

# Transfer 0.1 mg of boronic acid (solid) from bmida to rxn_well
transfer_solid(chmspd=chmspd, source=bmida, destination=rxn_well, weight=0.1)

# Transfer 0.1 mg of halide (solid) from halide to rxn_well
transfer_solid(chmspd=chmspd, source=halide, destination=rxn_well, weight=0.1)

# Transfer 0.1 mg of base (solid) from base to rxn_well
transfer_solid(chmspd=chmspd, source=base, destination=rxn_well, weight=0.1)

# Perform Schlenk cycles on rxn_well with 60 sec evacuation and 30 sec backfill_time
do_schlenk_cycles(chmspd=chmspd, wells=rxn_well, evac_time=60, backfill_time=30)

# Transfer 0.1 mL of catalyst solution from catalyst_solution to rxn_well with needle 1
transfer_liquid(chmspd=chmspd, source=catalyst_solution, destination=rxn_well, volume=0.1, needle=1)

# Transfer 1.0 mL of solvent from solvent to rxn_well with needle 1
transfer_liquid(chmspd=chmspd, source=solvent, destination=rxn_well, volume=1.0, needle=1)

# Transfer 1.0 mL of water from water to rxn_well with needle 4
transfer_liquid(chmspd=chmspd, source=water, destination=rxn_well, volume=1.0, needle=4)

# Reflux rxn_well at 100 rpm, 100 C, heat and cool 1 hour and condenser temperature at 20 C
heat_under_reflux(chmspd=chmspd, wells=rxn_well, stir_rate=100, temperature=100, heating_hours=1, cooling_hours=1, condenser_temperature=20)

# Transfer 10 mL of internal standard (liquid) from internal_standard to rxn_well with needle 1
transfer_liquid(chmspd=chmspd, source=internal_standard, destination=rxn_well, volume=10, needle=1)

# Filter 3 mL liquid sourced from rxn_well. Use filter_cartridge as filtration rack
filter_liquid(chmspd=chmspd, source_well=rxn_well, filtration_zone=filter_cartridge, filtration_volume=3)

# Transfer 3.0 mL of THF (liquid) from thf into filter_cartridge with needle 1
transfer_liquid(chmspd=chmspd, source=thf, destination=filter_cartridge, volume=3.0, needle=1)

# Transfer 0.2 mL liquid from filtrate_well to hplc_port with needle 1
transfer_liquid(chmspd=chmspd, source=filtrate_well, destination=hplc_port, volume=0.2, needle=1)
"""
