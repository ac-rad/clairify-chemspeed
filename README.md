# CLAIRify-Chemspeed
LLM-based code generation for Chemspyd

## Usage
### Install
```
pip install -r requirements.txt
```

### Run
1. Get your OpenAI API key and set up the `OPENAI_API_KEY` environment variable. Please refer to [Best Practices for API Key Safety](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) for details.
2. Run server
```
python flask_webserver.py
```
3. Open a browser and access to `http://127.0.0.1:3000`.
![Screenshot from 2023-11-05 15-32-04](https://github.com/ac-rad/clairify-chemspeed/assets/29328746/d6fcbc86-e5f1-4680-b97f-74f09e5f5ada)

### Example
#### Input
```
Prime pump 1 with 30 mL using chemspd as manager.
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
```

#### Output
```
routines.prime_pumps(chmspd=chmspd, pump=1, volume=30)
chemspd.transfer_liquid(source=thf, destination=internal_standard, volume=10, needle=1)
chemspd.transfer_solid(source=bmida, destination=rxn_well, weight=0.1)
chemspd.transfer_solid(source=halide, destination=rxn_well, weight=0.1)
chemspd.transfer_solid(source=base, destination=rxn_well, weight=0.1)
routines.do_schlenk_cycles(chmspd=chmspd, wells=rxn_well, evac_time=60, backfill_time=30)
chemspd.transfer_liquid(source=catalyst_solution, destination=rxn_well, volume=0.1, needle=1)
chemspd.transfer_liquid(source=solvent, destination=rxn_well, volume=1.0, needle=1)
chemspd.transfer_liquid(source=water, destination=rxn_well, volume=1.0, needle=4)
routines.heat_under_reflux(chmspd=chmspd, wells=rxn_well, stir_rate=100, temperature=100, heating_hours=1, cooling_hours=1, condenser_temperature=20)
chemspd.transfer_liquid(source=internal_standard, destination=rxn_well, volume=10, needle=1)
routines.filter_liquid(chmspd=chmspd, source_well=rxn_well, filtration_zone=filter_cartridge, filtration_volume=3)
chemspd.transfer_liquid(source=thf, destination=filter_cartridge, volume=3.0, needle=1)
chemspd.transfer_liquid(source=filtrate_well, destination=hplc_port, volume=0.2, needle=1)
```
