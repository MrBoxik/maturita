from __future__ import annotations

import json
import math
import random
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    import pypdfium2 as pdfium
except Exception:
    pdfium = None


APP_TITLE = "Motor Quiz"
WINDOW_SIZE = "1180x860"
BG = "#F6F8FB"
CARD = "#FFFFFF"
NAVY = "#17324D"
BLUE = "#2563EB"
TEAL = "#0F766E"
GREEN = "#2E8B57"
RED = "#C53030"
AMBER = "#B7791F"
LINE = "#D8E1EA"
MUTED = "#52606D"
INK = "#1F2937"


@dataclass(frozen=True)
class MotorSpec:
    power_kw: float
    poles: int
    rpm: int
    eta: float
    cosphi: float
    current: float


@dataclass(frozen=True)
class ABCQuestion:
    qid: str
    prompt: str
    options: tuple[str, str, str]
    correct_index: int
    explanation: str
    category: str


@dataclass(frozen=True)
class TestScenario:
    test_id: int
    title: str
    saw: dict
    pump: dict
    compressor: dict
    fan: dict
    beta: float = 0.6


MOTOR_CATALOG: dict[int, list[MotorSpec]] = {
    2: [
        MotorSpec(0.25, 2, 2830, 0.65, 0.82, 0.68),
        MotorSpec(0.37, 2, 2740, 0.66, 0.82, 1.00),
        MotorSpec(0.55, 2, 2800, 0.71, 0.82, 1.36),
        MotorSpec(0.75, 2, 2855, 0.73, 0.86, 1.73),
        MotorSpec(1.1, 2, 2845, 0.77, 0.87, 2.40),
        MotorSpec(1.5, 2, 2860, 0.79, 0.85, 3.25),
        MotorSpec(2.2, 2, 2880, 0.82, 0.85, 4.55),
        MotorSpec(3.0, 2, 2890, 0.84, 0.85, 6.10),
        MotorSpec(4.0, 2, 2905, 0.86, 0.86, 7.80),
        MotorSpec(5.5, 2, 2925, 0.865, 0.89, 10.30),
        MotorSpec(7.5, 2, 2930, 0.88, 0.89, 13.80),
        MotorSpec(11.0, 2, 2940, 0.895, 0.88, 20.00),
        MotorSpec(15.0, 2, 2940, 0.90, 0.90, 26.50),
        MotorSpec(18.5, 2, 2940, 0.91, 0.91, 32.50),
        MotorSpec(22.0, 2, 2945, 0.914, 0.86, 40.50),
    ],
    4: [
        MotorSpec(0.25, 4, 1350, 0.60, 0.79, 0.76),
        MotorSpec(0.37, 4, 1370, 0.65, 0.80, 1.03),
        MotorSpec(0.55, 4, 1395, 0.67, 0.82, 1.45),
        MotorSpec(0.75, 4, 1395, 0.72, 0.81, 1.86),
        MotorSpec(1.1, 4, 1415, 0.77, 0.81, 2.55),
        MotorSpec(1.5, 4, 1420, 0.79, 0.81, 3.40),
        MotorSpec(2.2, 4, 1420, 0.825, 0.82, 4.70),
        MotorSpec(3.0, 4, 1420, 0.83, 0.82, 6.40),
        MotorSpec(4.0, 4, 1440, 0.855, 0.83, 8.20),
        MotorSpec(5.5, 4, 1455, 0.86, 0.81, 11.40),
        MotorSpec(7.5, 4, 1455, 0.87, 0.82, 15.20),
        MotorSpec(11.0, 4, 1460, 0.885, 0.84, 21.50),
        MotorSpec(15.0, 4, 1460, 0.90, 0.84, 28.50),
        MotorSpec(18.5, 4, 1465, 0.904, 0.84, 35.00),
        MotorSpec(22.0, 4, 1465, 0.908, 0.84, 41.50),
    ],
    6: [
        MotorSpec(0.25, 6, 850, 0.61, 0.76, 0.78),
        MotorSpec(0.37, 6, 920, 0.62, 0.72, 1.20),
        MotorSpec(0.55, 6, 910, 0.67, 0.74, 1.60),
        MotorSpec(0.75, 6, 915, 0.69, 0.76, 2.10),
        MotorSpec(1.1, 6, 915, 0.72, 0.77, 2.90),
        MotorSpec(1.5, 6, 925, 0.74, 0.75, 3.90),
        MotorSpec(2.2, 6, 940, 0.78, 0.78, 5.20),
        MotorSpec(3.0, 6, 950, 0.79, 0.76, 7.20),
        MotorSpec(4.0, 6, 950, 0.805, 0.76, 9.40),
        MotorSpec(5.5, 6, 950, 0.83, 0.76, 12.80),
        MotorSpec(7.5, 6, 960, 0.86, 0.74, 17.00),
        MotorSpec(11.0, 6, 960, 0.875, 0.74, 24.50),
        MotorSpec(15.0, 6, 970, 0.889, 0.83, 29.50),
        MotorSpec(18.5, 6, 975, 0.898, 0.81, 36.50),
        MotorSpec(22.0, 6, 975, 0.903, 0.81, 43.50),
    ],
}

CABLE_AMPACITY = {
    "C": {1.0: 13.5, 1.5: 17.5, 2.5: 24.0, 4.0: 32.0, 6.0: 41.0, 10.0: 57.0, 16.0: 76.0},
    "D": {1.0: 14.5, 1.5: 18.0, 2.5: 24.0, 4.0: 31.0, 6.0: 39.0, 10.0: 52.0, 16.0: 67.0},
}

CABLE_PROTECTION_LIMIT = {
    "A": {1.0: 6, 1.5: 10, 2.5: 16, 4.0: 20, 6.0: 25, 10.0: 32, 16.0: 50},
    "B": {1.0: 6, 1.5: 10, 2.5: 16, 4.0: 20, 6.0: 25, 10.0: 32, 16.0: 50},
    "C": {1.0: 10, 1.5: 10, 2.5: 16, 4.0: 25, 6.0: 32, 10.0: 50, 16.0: 63},
    "D": {1.0: 0, 1.5: 10, 2.5: 20, 4.0: 25, 6.0: 32, 10.0: 40, 16.0: 50},
    "E": {1.0: 0, 1.5: 10, 2.5: 16, 4.0: 25, 6.0: 32, 10.0: 50, 16.0: 63},
}

BREAKER_SERIES = [6, 10, 16, 20, 25, 32, 40, 50, 63]
SECTIONS = [1.0, 1.5, 2.5, 4.0, 6.0, 10.0, 16.0]
RHO_CU = 0.0175


def bundle_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")).resolve()
    return Path(__file__).resolve().parent


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


STATE_FILE = app_dir() / "motor_quiz_state.json"
ICON_FILE = bundle_dir() / "app_icon.ico"


def format_num(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def format_section(section: float) -> str:
    return f"{int(section) if float(section).is_integer() else str(section).replace('.', ',')} mm²"


def prettify_symbols(text: str) -> str:
    replacements = {
        "P_h": "Pₕ",
        "P_k": "Pₖ",
        "P_v": "Pᵥ",
        "I_n": "Iₙ",
        "I_z": "Iᶻ",
        "P1": "P₁",
        "P2": "P₂",
        "U1": "U₁",
        "U2": "U₂",
        "R1": "R₁",
        "R2": "R₂",
    }
    result = text
    for source, target in replacements.items():
        result = result.replace(source, target)
    return result


def poles_from_rpm(rpm: float) -> int:
    references = {2: 2900, 4: 1450, 6: 950}
    return min(references, key=lambda poles: abs(references[poles] - rpm))


def choose_motor(required_kw: float, rpm: float) -> MotorSpec:
    poles = poles_from_rpm(rpm)
    for motor in MOTOR_CATALOG[poles]:
        if motor.power_kw >= required_kw:
            return motor
    return MOTOR_CATALOG[poles][-1]


def cable_resistance(length_m: float, section_mm2: float) -> float:
    return RHO_CU * length_m / section_mm2


def voltage_drop(current_a: float, resistance_ohm: float, cosphi: float) -> tuple[float, float]:
    drop_v = math.sqrt(3) * current_a * resistance_ohm * cosphi
    return drop_v, drop_v / 400 * 100


def protection_current_for_section(installation: str, section: float) -> int:
    return int(CABLE_PROTECTION_LIMIT[installation][section])


def choose_cable_section(current_a: float, installation: str, length_m: float, cosphi: float) -> tuple[float, float, float]:
    for section in SECTIONS:
        if CABLE_AMPACITY[installation][section] < current_a:
            continue
        if protection_current_for_section(installation, section) < current_a:
            continue
        resistance = cable_resistance(length_m, section)
        _, drop_pct = voltage_drop(current_a, resistance, cosphi)
        if drop_pct <= 5.0:
            return section, resistance, drop_pct
    section = SECTIONS[-1]
    resistance = cable_resistance(length_m, section)
    _, drop_pct = voltage_drop(current_a, resistance, cosphi)
    return section, resistance, drop_pct


def choose_breaker(installation: str, section: float, characteristic: str = "C") -> str:
    return f"{characteristic}{protection_current_for_section(installation, section)}"


def solve_saw(data: dict) -> dict:
    required_kw = data["force_n"] * data["speed_ms"] / 1000
    rpm = 60 * data["speed_ms"] / (math.pi * data["diameter_m"])
    motor = choose_motor(required_kw, rpm)
    section, resistance, drop_pct = choose_cable_section(motor.current, data["installation"], data["length_m"], motor.cosphi)
    breaker = choose_breaker(data["installation"], section)
    return {
        "type": "pila",
        "required_kw": required_kw,
        "rpm": rpm,
        "motor": motor,
        "section": section,
        "resistance": resistance,
        "drop_pct": drop_pct,
        "breaker": breaker,
        "installation": data["installation"],
        "task_text": f"d = {format_num(data['diameter_m'],2)} m, v = {format_num(data['speed_ms'],0)} m/s, F = {format_num(data['force_n'],0)} N, l = {format_num(data['length_m'],0)} m, uložení {data['installation']}",
    }


def solve_pump(data: dict) -> dict:
    q_m3s = data["flow_lps"] / 1000
    ph_kw = 1000 * 9.81 * q_m3s * data["head_m"] / 1000
    required_kw = ph_kw / data["task_eta"]
    motor = choose_motor(required_kw, data["rpm"])
    section, resistance, drop_pct = choose_cable_section(motor.current, data["installation"], data["length_m"], motor.cosphi)
    breaker = choose_breaker(data["installation"], section)
    return {
        "type": "cerpadlo",
        "required_kw": required_kw,
        "rpm": data["rpm"],
        "motor": motor,
        "section": section,
        "resistance": resistance,
        "drop_pct": drop_pct,
        "breaker": breaker,
        "installation": data["installation"],
        "hydraulic_kw": ph_kw,
        "task_text": f"Q = {format_num(data['flow_lps'],0)} l/s, H = {format_num(data['head_m'],0)} m, η = {format_num(data['task_eta']*100,0)} %, n = {format_num(data['rpm'],0)} ot/min, l = {format_num(data['length_m'],0)} m, uložení {data['installation']}",
    }


def solve_compressor(data: dict) -> dict:
    required_kw = data["pk_kw"] / data["task_eta"]
    motor = choose_motor(required_kw, data["rpm"])
    section, resistance, drop_pct = choose_cable_section(motor.current, data["installation"], data["length_m"], motor.cosphi)
    breaker = choose_breaker(data["installation"], section)
    return {
        "type": "kompresor",
        "required_kw": required_kw,
        "rpm": data["rpm"],
        "motor": motor,
        "section": section,
        "resistance": resistance,
        "drop_pct": drop_pct,
        "breaker": breaker,
        "installation": data["installation"],
        "task_text": f"Pₖ = {format_num(data['pk_kw'],1)} kW, η = {format_num(data['task_eta']*100,0)} %, n = {format_num(data['rpm'],0)} ot/min, l = {format_num(data['length_m'],0)} m, uložení {data['installation']}",
    }


def solve_fan(data: dict) -> dict:
    required_kw = data["pv_kw"]
    motor = choose_motor(required_kw, data["rpm"])
    section, resistance, drop_pct = choose_cable_section(motor.current, data["installation"], data["length_m"], motor.cosphi)
    breaker = choose_breaker(data["installation"], section)
    return {
        "type": "ventilator",
        "required_kw": required_kw,
        "rpm": data["rpm"],
        "motor": motor,
        "section": section,
        "resistance": resistance,
        "drop_pct": drop_pct,
        "breaker": breaker,
        "installation": data["installation"],
        "task_text": f"Pᵥ = {format_num(data['pv_kw'],1)} kW, n = {format_num(data['rpm'],0)} ot/min, l = {format_num(data['length_m'],0)} m, uložení {data['installation']}",
    }


def solve_full_test(test: TestScenario) -> dict:
    saw = solve_saw(test.saw)
    pump = solve_pump(test.pump)
    compressor = solve_compressor(test.compressor)
    fan = solve_fan(test.fan)
    p1_sum = sum(item["motor"].power_kw / item["motor"].eta for item in [saw, pump, compressor, fan])
    simultaneous = test.beta * p1_sum
    return {
        "saw": saw,
        "pump": pump,
        "compressor": compressor,
        "fan": fan,
        "simultaneous_kw": simultaneous,
        "beta": test.beta,
    }


def generate_test_scenarios() -> list[TestScenario]:
    tests = [
        TestScenario(
            1,
            "Test 01 | Originál",
            {"force_n": 200, "speed_ms": 30, "diameter_m": 0.4, "length_m": 70, "installation": "C"},
            {"flow_lps": 20, "head_m": 15, "task_eta": 0.70, "rpm": 2900, "length_m": 100, "installation": "D"},
            {"pk_kw": 4.0, "task_eta": 0.60, "rpm": 2800, "length_m": 100, "installation": "C"},
            {"pv_kw": 3.0, "rpm": 2850, "length_m": 75, "installation": "D"},
        )
    ]
    rng = random.Random(20260410)
    saw_forces = [150, 160, 170, 180, 190, 205, 220, 240, 260]
    saw_speeds = [25, 27, 28, 29, 30, 31, 32, 33]
    saw_diams = [0.22, 0.35, 0.37, 0.39, 0.40, 0.42, 0.45]
    saw_lengths = [45, 55, 60, 65, 70, 75, 85, 95]
    pump_flows = [10, 12, 14, 16, 18, 20, 22, 24, 28]
    pump_heads = [12, 14, 15, 16, 18, 19, 21, 22]
    pump_etas = [0.62, 0.65, 0.68, 0.70, 0.72]
    pump_rpms = [1450, 2900]
    pump_lengths = [60, 75, 85, 95, 100, 110, 120, 130]
    comp_pks = [3.5, 4.0, 4.2, 4.5, 5.0, 5.5, 6.0, 6.5]
    comp_etas = [0.58, 0.60, 0.62, 0.65, 0.68, 0.72]
    comp_rpms = [1450, 2800]
    comp_lengths = [55, 70, 80, 90, 100, 110, 120, 130]
    fan_powers = [1.5, 2.2, 3.0, 4.0, 5.5]
    fan_rpms = [950, 1410, 2850]
    fan_lengths = [35, 45, 55, 65, 75, 85, 95, 110]
    betas = [0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
    for idx in range(2, 21):
        tests.append(
            TestScenario(
                idx,
                f"Test {idx:02d}",
                {
                    "force_n": rng.choice(saw_forces),
                    "speed_ms": rng.choice(saw_speeds),
                    "diameter_m": rng.choice(saw_diams),
                    "length_m": rng.choice(saw_lengths),
                    "installation": rng.choice(["C", "C", "C", "D"]),
                },
                {
                    "flow_lps": rng.choice(pump_flows),
                    "head_m": rng.choice(pump_heads),
                    "task_eta": rng.choice(pump_etas),
                    "rpm": rng.choice(pump_rpms),
                    "length_m": rng.choice(pump_lengths),
                    "installation": rng.choice(["D", "D", "D", "C"]),
                },
                {
                    "pk_kw": rng.choice(comp_pks),
                    "task_eta": rng.choice(comp_etas),
                    "rpm": rng.choice(comp_rpms),
                    "length_m": rng.choice(comp_lengths),
                    "installation": rng.choice(["C", "C", "C", "D"]),
                },
                {
                    "pv_kw": rng.choice(fan_powers),
                    "rpm": rng.choice(fan_rpms),
                    "length_m": rng.choice(fan_lengths),
                    "installation": rng.choice(["D", "D", "C"]),
                },
                rng.choice(betas),
            )
        )
    return tests


ALL_TESTS = generate_test_scenarios()
ALL_SOLUTIONS = {test.test_id: solve_full_test(test) for test in ALL_TESTS}


def make_option_question(qid: str, prompt: str, correct: str, wrong_a: str, wrong_b: str, explanation: str, category: str, rng: random.Random) -> ABCQuestion:
    prompt = prettify_symbols(prompt)
    correct = prettify_symbols(correct)
    wrong_a = prettify_symbols(wrong_a)
    wrong_b = prettify_symbols(wrong_b)
    explanation = prettify_symbols(explanation)
    options = [correct, wrong_a, wrong_b]
    rng.shuffle(options)
    return ABCQuestion(qid, prompt, tuple(options), options.index(correct), explanation, category)


def generate_abc_questions() -> list[ABCQuestion]:
    rng = random.Random(1337)
    questions: list[ABCQuestion] = []

    symbol_questions = [
        ("Q001", "Co znamená P_h?", "hydraulický výkon čerpadla", "příkon hlavního jističe", "jmenovitý proud motoru", "P_h se používá u čerpadla a značí hydraulický výkon."),
        ("Q002", "Co znamená P_k?", "výkon kompresoru ze zadání", "výkon kabelu", "výkon kotouče pily", "P_k je výkon kompresoru ze zadání."),
        ("Q003", "Co znamená P_v?", "výkon ventilátoru", "výstupní napětí", "pokles výkonu", "P_v značí výkon ventilátoru."),
        ("Q004", "Co znamená I_n?", "jmenovitý proud motoru", "maximální dovolený úbytek", "izolační odpor", "I_n je jmenovitý proud motoru."),
        ("Q005", "Co znamená β?", "součinitel současnosti", "účinnost motoru", "počet pólů", "β používáš při výpočtu současného příkonu."),
        ("Q006", "Jaké dvě různé veličiny se schovávají pod ρ?", "hustota a měrný odpor", "výkon a proud", "otáčky a napětí", "U čerpadla je ρ hustota, u kabelu ρ měrný odpor."),
        ("Q007", "Co znamená P1?", "elektrický příkon ze sítě", "mechanický výkon na hřídeli", "výkon pily", "P1 je příkon motoru ze sítě."),
        ("Q008", "Co znamená P2?", "výkon na hřídeli motoru", "současný příkon", "proud jedné fáze", "P2 je výkon motoru na hřídeli."),
        ("Q009", "Co znamená cos φ?", "účiník", "účinnost", "soudobost", "cos φ je účiník motoru."),
        ("Q010", "Co znamená η?", "účinnost", "účiník", "úbytek napětí", "η značí účinnost."),
    ]
    for qid, prompt, c, a, b, e in symbol_questions:
        questions.append(make_option_question(qid, prompt, c, a, b, e, "Značky", rng))

    table_questions = [
        ("Q011", "Na co používáš tabulku 1?", "na výběr motoru podle výkonu, pólů, η, cosφ a I_n", "na převod l/s na m³/s", "na výběr barev vodičů", "Tabulka 1 je katalog motorů."),
        ("Q012", "Na co používáš tabulku 2?", "na převod způsobu uložení kabelu na písmena A až E", "na výběr jističe podle proudu", "na výpočet současného příkonu", "Tabulka 2 převádí slovní popis uložení na písmeno."),
        ("Q013", "Na co používáš tabulku 4?", "na kontrolu, zda kabel unese proud", "na zjištění otáček motoru", "na výpočet výkonu pily", "Tabulka 4 obsahuje dovolené zatěžovací proudy vodičů."),
        ("Q014", "Na co používáš tabulku 6?", "na výběr charakteristiky a velikosti jističe", "na převod mm² na m²", "na výběr průřezu kabelu", "Tabulka 6 je o jističích."),
        ("Q015", "Jaký popis se v těchto úlohách typicky převádí na uložení C?", "na stěně", "v trubce v zemi", "na volném vzduchu", "Na stěně bývá v těchto školních úlohách C."),
        ("Q016", "Jaký popis se typicky převádí na uložení D?", "v trubce v zemi", "na stěně", "v liště na dřevě", "V zemi nebo v trubce v zemi bývá D."),
        ("Q017", "Jakou tabulku potřebuješ pro kontrolu 1,5 mm² v uložení C?", "tabulku 4", "tabulku 1", "tabulku 10", "Proudová zatížitelnost je v tabulce 4."),
        ("Q018", "Kde najdeš cos φ motoru?", "v tabulce 1", "v tabulce 2", "v tabulce 6", "cos φ přebíráš z katalogu motorů v tabulce 1."),
        ("Q019", "Kde najdeš písmeno A až E pro uložení kabelu?", "v tabulce 2", "v tabulce 4", "v tabulce 1", "Tabulka 2 je přímo o uložení kabelů."),
        ("Q020", "Která tabulka ti pomůže s jističem C16 nebo C25?", "tabulka 6", "tabulka 1", "tabulka 8", "Typ a řada jističů je v tabulce 6."),
    ]
    for qid, prompt, c, a, b, e in table_questions:
        questions.append(make_option_question(qid, prompt, c, a, b, e, "Tabulky", rng))

    conversion_questions = [
        ("Q021", "Kolik je 20 l/s v m³/s?", "0,02 m³/s", "0,2 m³/s", "0,002 m³/s", "1 l/s = 0,001 m³/s, takže 20 l/s = 0,02 m³/s."),
        ("Q022", "Kolik je 1 l/s v m³/s?", "0,001 m³/s", "0,01 m³/s", "0,0001 m³/s", "1 litr je 0,001 m³."),
        ("Q023", "Kolik je 1,5 mm² v m²?", "1,5×10^-6 m²", "1,5×10^-3 m²", "1,5×10^-9 m²", "1 mm² = 10^-6 m²."),
        ("Q024", "Jakou školní hodnotu používáš pro měrný odpor mědi?", "0,0175 Ω·mm²/m", "17,5 Ω·mm²/m", "0,175 Ω·m/mm²", "Ve guideu používáš 0,0175 Ω·mm²/m."),
        ("Q025", "Když používáš ρ = 0,0175 Ω·mm²/m, v čem musí být S?", "v mm²", "v m²", "v cm²", "K jednotce ρ musí odpovídat průřez v mm²."),
        ("Q026", "Kolik je 5,5 kW ve wattech?", "5500 W", "55 W", "550 W", "1 kW = 1000 W."),
        ("Q027", "Kolik je 70 % v desetinném tvaru?", "0,70", "7,0", "0,07", "Účinnost ve vzorci používáš jako desetinné číslo."),
        ("Q028", "Kolik je 87 % v desetinném tvaru?", "0,87", "8,7", "0,087", "87 % = 0,87."),
        ("Q029", "Jaké napětí U používáš ve vzorci pro třífázový motor v těchto úlohách?", "400 V", "230 V", "690 V", "Guide počítá s třífázovou sítí 3×400/230 V."),
        ("Q030", "Jaký limit úbytku napětí se v úlohách typicky hlídá?", "5 %", "2 %", "10 %", "V guideu se všechny kabely kontrolují proti limitu 5 %."),
    ]
    for qid, prompt, c, a, b, e in conversion_questions:
        questions.append(make_option_question(qid, prompt, c, a, b, e, "Převody", rng))

    rule_questions = [
        ("Q031", "Motor s otáčkami kolem 3000 ot/min bývá:", "2pólový", "4pólový", "6pólový", "3000 ot/min ukazuje na 2 póly."),
        ("Q032", "Motor s otáčkami kolem 1500 ot/min bývá:", "4pólový", "2pólový", "6pólový", "1500 ot/min ukazuje na 4 póly."),
        ("Q033", "Motor s otáčkami kolem 1000 ot/min bývá:", "6pólový", "4pólový", "2pólový", "1000 ot/min ukazuje na 6 pólů."),
        ("Q034", "Jakou charakteristiku jističe většinou volíš pro motor?", "C", "B", "A", "U motorů obvykle volíš charakteristiku C."),
        ("Q035", "Co uděláš, když vyjde úbytek nad 5 %?", "zvětšíš průřez a přepočítáš", "snížíš výkon motoru", "změníš účiník v tabulce 1", "Úbytek nad limitem řešíš větším průřezem."),
        ("Q036", "Když ti vyjde potřebný výkon motoru 6,2 kW, co uděláš?", "vybereš nejbližší vyšší standardní výkon", "vybereš nejbližší nižší výkon", "necháš přesně 6,2 kW", "Motor se bere jako první vyšší standardní hodnota."),
        ("Q037", "Jaké dvě podmínky musí splnit kabel?", "proudovou zatížitelnost i úbytek napětí", "jen proudovou zatížitelnost", "jen správné uložení", "Kabel musí vyhovět proudově i napěťově."),
        ("Q038", "U kompresoru se často stane co?", "proudově kabel vyjde, ale úbytkem ne", "motor vždy vychází 4pólový", "jistič se volí B", "Právě kompresor typicky nutí korigovat průřez kvůli ΔU."),
        ("Q039", "Kdy počítáš současný příkon Pβ?", "až po vyřešení všech motorů", "ještě před výběrem prvního motoru", "místo výpočtu proudu motoru", "Současný příkon počítáš až úplně nakonec."),
        ("Q040", "Který údaj z tabulky 1 používáš do vzorce pro úbytek napětí?", "cos φ", "η v zadání čerpadla", "počet pólů", "Do ΔU vstupuje účiník cos φ motoru."),
    ]
    for qid, prompt, c, a, b, e in rule_questions:
        questions.append(make_option_question(qid, prompt, c, a, b, e, "Pravidla", rng))

    formula_questions = [
        ("Q041", "Který vzorec patří k pile?", "P = F·v", "P = P_k / η", "P_h = ρ·g·Q·H", "Pila používá P = F·v."),
        ("Q042", "Který vzorec patří k otáčkám kotouče?", "n = 60·v / (π·d)", "n = π·d / (60·v)", "n = U·I / η", "Otáčky kotouče počítáš z rychlosti a průměru."),
        ("Q043", "Který vzorec patří k čerpadlu?", "P_h = ρ·g·Q·H", "P = F·v", "P = U·I", "Hydraulický výkon čerpadla je ρ·g·Q·H."),
        ("Q044", "Který vzorec patří ke kompresoru?", "P = P_k / η", "P = η / P_k", "P = P_k·η²", "Potřebný výkon motoru kompresoru získáš dělením účinností."),
        ("Q045", "Který vzorec patří k jmenovitému proudu motoru?", "I_n = P2 / (√3·U·η·cosφ)", "I_n = U / (P2·η)", "I_n = η / (U·cosφ)", "Tohle je správný vztah pro třífázový motor."),
        ("Q046", "Který vzorec patří k odporu kabelu?", "R = ρ·l / S", "R = S / (ρ·l)", "R = U·I", "Odpor kabelu roste s délkou a klesá s průřezem."),
        ("Q047", "Který vzorec patří k úbytku napětí?", "ΔU = √3·I·R·cosφ", "ΔU = I / (√3·R)", "ΔU = P / U", "Guide používá zjednodušený vztah s odporem a účiníkem."),
        ("Q048", "Který vzorec patří k příkonu motoru?", "P1 = P2 / η", "P1 = P2·η", "P1 = U / I", "Příkon je vždy větší než výkon na hřídeli, proto dělíš účinností."),
        ("Q049", "Který vzorec patří k současnému příkonu?", "Pβ = β·ΣP1", "Pβ = ΣP2 / β", "Pβ = β / ΣP1", "Současný příkon je β krát součet příkonů."),
        ("Q050", "Když v úloze zanedbáš X_L, co používáš pro úbytek?", "jen odpor vodiče", "jen indukčnost", "odpor a kapacitu", "V zadání se často píše zanedbej X_L a uvažuj jen odpor vodiče."),
    ]
    for qid, prompt, c, a, b, e in formula_questions:
        questions.append(make_option_question(qid, prompt, c, a, b, e, "Vzorce", rng))

    numeric_questions = [
        ("Q051", "Kolik vyjde výkon pily při F = 200 N a v = 30 m/s?", "6,0 kW", "60 kW", "0,6 kW", "P = F·v = 200·30 = 6000 W = 6,0 kW."),
        ("Q052", "Kolik vyjde výkon motoru kompresoru při P_k = 4 kW a η = 60 %?", "6,67 kW", "2,40 kW", "4,60 kW", "P = 4 / 0,60 = 6,67 kW."),
        ("Q053", "Kolik vyjde hydraulický výkon čerpadla při Q = 20 l/s a H = 15 m?", "2,94 kW", "29,4 kW", "0,294 kW", "Po převodu Q = 0,02 m³/s vyjde P_h ≈ 2,943 kW."),
        ("Q054", "Kolik vyjde potřebný výkon motoru čerpadla při P_h = 2,943 kW a η = 70 %?", "4,20 kW", "2,06 kW", "7,50 kW", "P = 2,943 / 0,70 = 4,20 kW."),
        ("Q055", "Pila má d = 0,4 m a v = 30 m/s. Jaké otáčky kotouče zhruba vyjdou?", "1430 ot/min", "2860 ot/min", "950 ot/min", "n = 60·30 / (π·0,4) ≈ 1432 ot/min."),
        ("Q056", "Jaký proud zhruba vyjde pro motor 5,5 kW, η = 0,865, cosφ = 0,89?", "10,3 A", "5,3 A", "18,0 A", "I_n = 5500 / (√3·400·0,865·0,89) ≈ 10,3 A."),
        ("Q057", "Jaký odpor má kabel 70 m, 1,5 mm²?", "0,817 Ω", "8,17 Ω", "0,0817 Ω", "R = 0,0175·70 / 1,5 = 0,817 Ω."),
        ("Q058", "Jaký úbytek vyjde přibližně pro pilu v originálním příkladu?", "4,4 %", "1,4 %", "8,4 %", "Pro I = 15,2 A, R = 0,817 Ω a cosφ = 0,82 vyjde ΔU asi 4,4 %."),
        ("Q059", "Podle čeho v těchto příkladech určíš proud jističe?", "z tabulky 5 podle průřezu a uložení kabelu", "jen z nejbližšího vyššího proudu motoru", "jen z tabulky 1 bez kabelu", "Ve školním postupu vezmeš proud jističe z tabulky 5 a charakteristiku z tabulky 6."),
        ("Q060", "Když má ventilátor proud 6,1 A, jaký jistič zvolíš?", "C10", "C6", "B10", "6,1 A je nad 6 A, takže vyjde C10."),
    ]
    for qid, prompt, c, a, b, e in numeric_questions:
        questions.append(make_option_question(qid, prompt, c, a, b, e, "Výpočty", rng))

    cable_questions = []
    qnum = 61
    for installation in ["C", "D"]:
        for section, ampacity in [(1.5, CABLE_AMPACITY[installation][1.5]), (2.5, CABLE_AMPACITY[installation][2.5]), (4.0, CABLE_AMPACITY[installation][4.0]), (6.0, CABLE_AMPACITY[installation][6.0])]:
            wrong1 = CABLE_AMPACITY["D" if installation == "C" else "C"][section]
            wrong2 = CABLE_AMPACITY[installation][2.5 if section == 1.5 else 1.5]
            prompt = f"Jaký dovolený proud má zhruba kabel {format_section(section)} v uložení {installation} pro 3 zatížené vodiče?"
            explanation = f"V tabulce 4 je pro {format_section(section)} a uložení {installation} hodnota {format_num(ampacity,1)} A."
            cable_questions.append(
                make_option_question(
                    f"Q{qnum:03d}",
                    prompt,
                    f"{format_num(ampacity,1)} A",
                    f"{format_num(wrong1,1)} A",
                    f"{format_num(wrong2,1)} A",
                    explanation,
                    "Kabely",
                    rng,
                )
            )
            qnum += 1
    questions.extend(cable_questions)

    solved_cache = {test.test_id: solve_full_test(test) for test in ALL_TESTS}
    for test in ALL_TESTS[:12]:
        solved = solved_cache[test.test_id]
        saw = solved["saw"]
        pump = solved["pump"]
        comp = solved["compressor"]
        fan = solved["fan"]
        dynamic = [
            (
                f"Q{qnum:03d}",
                f"{test.title}: Jaký motor vyjde pro pilu?",
                f"{format_num(saw['motor'].power_kw,1)} kW / {saw['motor'].poles} póly",
                f"{format_num(max(0.75, saw['motor'].power_kw - 1.5),1)} kW / 2 póly",
                f"{format_num(saw['motor'].power_kw,1)} kW / {6 if saw['motor'].poles != 6 else 4} póly",
                f"Pro pilu v {test.title} vychází potřebný výkon {format_num(saw['required_kw'],2)} kW a otáčky ukazují na {saw['motor'].poles} póly.",
            ),
            (
                f"Q{qnum+1:03d}",
                f"{test.title}: Jaký průřez kabelu vyjde pro čerpadlo?",
                format_section(pump["section"]),
                format_section(max(1.0, pump["section"] - 1.0)),
                format_section(pump["section"] + 1.5),
                f"Čerpadlo v {test.title} potřebuje kabel {format_section(pump['section'])}; proudově i úbytkem to vyjde.",
            ),
            (
                f"Q{qnum+2:03d}",
                f"{test.title}: Jaký jistič vyjde pro kompresor?",
                comp["breaker"],
                f"C{max(6, int(comp['breaker'][1:]) - 6)}",
                f"B{comp['breaker'][1:]}",
                f"Kompresor má proud {format_num(comp['motor'].current,1)} A, proto vyjde {comp['breaker']}.",
            ),
            (
                f"Q{qnum+3:03d}",
                f"{test.title}: Jaký současný příkon Pβ vyjde pro celý test?",
                f"{format_num(solved['simultaneous_kw'],1)} kW",
                f"{format_num(solved['simultaneous_kw'] - 3.0,1)} kW",
                f"{format_num(solved['simultaneous_kw'] + 4.0,1)} kW",
                f"Současný příkon pro {test.title} vyjde {format_num(solved['simultaneous_kw'],2)} kW.",
            ),
        ]
        for qid, prompt, c, a, b, e in dynamic:
            questions.append(make_option_question(qid, prompt, c, a, b, e, "Příklady", rng))
        qnum += 4

    extra_questions = [
        ("Kdy vybereš 4pólový motor?", "když otáčky vyjdou kolem 1500 ot/min", "když je výkon nad 7,5 kW", "když je kabel v zemi", "Počet pólů určuješ z otáček, ne z kabelu nebo výkonu."),
        ("Kdy vybereš 2pólový motor?", "když otáčky vyjdou kolem 3000 ot/min", "když je účinnost 90 %", "když je v zadání ventilátor", "2 póly poznáš z otáček kolem 3000 ot/min."),
        ("Co musíš opsat z tabulky 1 po výběru motoru?", "n, η, cosφ a I_n", "jen barvy vodičů", "jen průřez kabelu", "Po výběru motoru tě z tabulky 1 zajímá hlavně n, η, cosφ a I_n."),
        ("Co je nejčastější chyba u čerpadla?", "nepřevést l/s na m³/s", "volit jistič B místo C", "počítat odpor bez π", "U čerpadla se často zapomene převést průtok."),
        ("Co je nejčastější chyba u kompresoru?", "nezkontrolovat úbytek napětí po výběru průřezu", "vybírat 6pólový motor", "počítat P = F·v", "U kompresoru proudově kabel často vyjde, ale úbytkem ne."),
        ("Co je nejčastější chyba u úbytku napětí?", "pomíchat jednotky u ρ a S", "zapomenout počet pólů", "počítat β místo cosφ", "Když ρ dáš v Ω·mm²/m, musí být S v mm²."),
        ("Jaké napětí používáš v procentech úbytku napětí?", "400 V", "230 V", "690 V", "V guideu se procentní úbytek počítá jako ΔU/400·100."),
        ("Jakou hodnotu β používá guide v příkladech?", "0,6", "1,0", "0,3", "Guide počítá se soudobostí β = 0,6."),
        ("Jak se spočítá P1 jednoho motoru?", "P1 = P2 / η", "P1 = η / P2", "P1 = P2·cosφ", "P1 je příkon ze sítě, takže dělíš výkon účinností."),
        ("Kdy bereš z tabulky 1 2pólový a 4pólový řádek?", "podle otáček", "podle délky kabelu", "podle úbytku napětí", "Rozhodující jsou otáčky, ne kabel."),
    ]
    for prompt, c, a, b, e in extra_questions:
        questions.append(make_option_question(f"Q{qnum:03d}", prompt, c, a, b, e, "Opakování", rng))
        qnum += 1

    return questions


def generate_practical_abc_questions() -> list[ABCQuestion]:
    rng = random.Random()
    questions: list[ABCQuestion] = []
    qnum = 1

    def add(prompt: str, correct: str, wrong_a: str, wrong_b: str, explanation: str, category: str) -> None:
        nonlocal qnum
        questions.append(
            make_option_question(f"A{qnum:03d}", prompt, correct, wrong_a, wrong_b, explanation, category, rng)
        )
        qnum += 1

    symbol_questions = [
        ("Co znamená P_h?", "hydraulický výkon čerpadla", "příkon hlavního jističe", "proud na hřídeli", "P_h používáš u čerpadla pro výkon kapaliny.", "Značky"),
        ("Co znamená P_k?", "výkon kompresoru ze zadání", "výkon kabelu", "ztrátový výkon motoru", "P_k je výkon, který potřebuje kompresor.", "Značky"),
        ("Co znamená P_v?", "výkon ventilátoru", "výstupní napětí", "pokles výkonu", "P_v je výkon ventilátoru ze zadání.", "Značky"),
        ("Co znamená P1?", "elektrický příkon motoru ze sítě", "mechanický výkon na hřídeli", "současný příkon celé soustavy", "P₁ je vstupní elektrický příkon.", "Značky"),
        ("Co znamená P2?", "mechanický výkon na hřídeli motoru", "příkon jističe", "výkon přívodního kabelu", "P₂ je výkon, který motor dává ven na hřídeli.", "Značky"),
        ("Co znamená I_n?", "jmenovitý proud motoru", "dovolený proud kabelu", "okamžitý rozběhový proud", "Iₙ bereš z katalogu motoru nebo dopočítáš.", "Značky"),
        ("Co znamená dovolený zatěžovací proud kabelu?", "proud, který kabel bezpečně unese", "jmenovitý proud motoru", "zkratový proud", "Je to maximální proud, který kabel při daném uložení bezpečně snese.", "Značky"),
        ("Co znamená η?", "účinnost", "účiník", "soudobost", "Účinnost porovnává výstupní výkon a příkon.", "Značky"),
        ("Co znamená cos φ?", "účiník", "účinnost", "součinitel současnosti", "cos φ používáš u proudu a úbytku napětí.", "Značky"),
        ("Co znamená β?", "součinitel současnosti", "účinnost kabelu", "počet pólů", "β používáš až u současného příkonu celé soustavy.", "Značky"),
        ("Co znamená Q?", "průtok", "náboj", "činitel jakosti", "U čerpadla je Q průtok kapaliny.", "Značky"),
        ("Co znamená H?", "dopravní výška", "hlavní jistič", "hloubka uložení kabelu", "U čerpadla H značí výšku, do které vodu zvedáš.", "Značky"),
        ("Co znamená n?", "otáčky", "počet fází", "normovaný výkon", "n je počet otáček za minutu.", "Značky"),
        ("Co znamená S v kabelovém výpočtu?", "průřez vodiče", "délku vedení", "současný příkon", "S je průřez jádra vodiče.", "Značky"),
        ("Co znamená R v kabelovém výpočtu?", "odpor vedení", "otáčky motoru", "mechanický odpor stroje", "R je elektrický odpor kabelu.", "Značky"),
    ]
    for item in symbol_questions:
        add(*item)

    workflow_questions = [
        ("U pily znáš řeznou sílu a řeznou rychlost. Co počítáš jako první?", "potřebný výkon P2", "úbytek napětí na kabelu", "současný příkon celé soustavy", "U pily nejdřív zjistíš, jaký výkon musí dodat motor.", "Postup"),
        ("U pily po výpočtu výkonu ještě potřebuješ zjistit:", "otáčky podle průměru kotouče a rychlosti", "účinnost kabelu", "hodnotu β", "Počet pólů motoru vybíráš podle otáček.", "Postup"),
        ("U čerpadla před výpočtem P_h musíš nejdřív:", "převést průtok z l/s na m³/s", "převést napětí z 400 V na 230 V", "převést délku kabelu na km", "Bez převodu Q by vyšel hydraulický výkon špatně.", "Postup"),
        ("Když máš u čerpadla vypočtený hydraulický výkon P_h, další krok je:", "vydělit ho účinností a získat P2", "vynásobit ho cos φ", "rovnou vybrat jistič", "Motor musí dodat víc než samotný hydraulický výkon, proto dělíš účinností.", "Postup"),
        ("U kompresoru se potřebný výkon motoru běžně určí tak, že:", "P_k vydělíš účinností", "P_k vynásobíš cos φ", "P_k vydělíš napětím", "Když má stroj účinnost menší než 1, motor musí mít vyšší výkon než samotný kompresor.", "Postup"),
        ("U ventilátoru v těchto úlohách bývá potřebný výkon motoru obvykle:", "rovný P_v", "rovný P_v / cos φ", "rovný P_v · β", "U ventilátoru se většinou výkon bere přímo ze zadání.", "Postup"),
        ("Když ti vyjde potřebný výkon motoru 6,2 kW, co uděláš?", "vezmeš nejbližší vyšší standardní motor", "vezmeš nejbližší nižší motor", "neřešíš standardní řady a necháš 6,2 kW", "Motor nesmí být slabší než požadavek, proto bereš vyšší standardní velikost.", "Postup"),
        ("Po výběru konkrétního motoru si z katalogu potřebuješ vzít hlavně:", "otáčky, účinnost, účiník a jmenovitý proud", "barvu vodičů a způsob uložení", "jen počet pólů a nic víc", "Pro kabel, proud i jistič potřebuješ η, cos φ a Iₙ.", "Postup"),
        ("Kabel musí vyhovět podle pravidel v těchto úlohách čemu?", "proudu i úbytku napětí", "jen proudu", "jen délce vedení", "Správný kabel musí unést proud a zároveň mít přijatelný úbytek napětí.", "Postup"),
        ("Když kabel proudově vyjde, ale úbytek napětí je nad limitem, uděláš co?", "zvětšíš průřez a přepočítáš", "necháš to být", "zmenšíš jistič", "U úbytku napětí pomůže menší odpor, tedy větší průřez.", "Postup"),
        ("Jistič pro motor v těchto úlohách obvykle volíš s charakteristikou:", "C", "B", "A", "Motor má rozběh, proto se běžně volí charakteristika C.", "Postup"),
        ("Současný příkon Pβ počítáš kdy?", "až po vyřešení všech motorů", "hned na začátku před výběrem motorů", "místo výpočtu proudu", "Nejdřív musíš znát P₁ každého motoru a až pak děláš soudobost.", "Postup"),
    ]
    for item in workflow_questions:
        add(*item)

    formula_questions = [
        ("Máš řeznou sílu F a rychlost v. Jaký vztah použiješ pro výkon pily?", "P = F·v", "P = U·I", "P = P_k / η", "Výkon pily určuje mechanický vztah síla krát rychlost.", "Vzorce"),
        ("Máš průměr kotouče d a obvodovou rychlost v. Jak spočítáš otáčky?", "n = 60·v / (π·d)", "n = π·d / (60·v)", "n = P / U", "Otáčky kotouče získáš z obvodové rychlosti a průměru.", "Vzorce"),
        ("Máš průtok Q a dopravní výšku H. Jaký vztah patří k čerpadlu?", "P_h = ρ·g·Q·H", "P = F·v", "P1 = P2·η", "Hydraulický výkon závisí na hustotě, gravitaci, průtoku a výšce.", "Vzorce"),
        ("Máš výkon kompresoru P_k a účinnost η. Jak určíš požadovaný výkon motoru?", "P2 = P_k / η", "P2 = P_k·η", "P2 = U·I", "Motor musí dodat víc než samotný stroj, proto dělíš účinností.", "Vzorce"),
        ("Jaký vztah použiješ pro jmenovitý proud třífázového motoru?", "I_n = P2 / (√3·U·η·cosφ)", "I_n = U / (P2·η)", "I_n = P2·η·cosφ", "Do proudu vstupuje výkon, napětí, účinnost i účiník.", "Vzorce"),
        ("Jak spočítáš odpor kabelu délky l a průřezu S?", "R = ρ·l / S", "R = S / (ρ·l)", "R = U·I", "Odpor roste s délkou a klesá s průřezem.", "Vzorce"),
        ("Jak spočítáš úbytek napětí, když zanedbáš reaktanci?", "ΔU = √3·I·R·cosφ", "ΔU = I / (√3·R)", "ΔU = P / U", "V těchto školních úlohách se často bere jen odpor vodiče.", "Vzorce"),
        ("Jak převedeš úbytek napětí na procenta v třífázové síti 400 V?", "ΔU% = ΔU / 400 · 100", "ΔU% = ΔU / 230 · 100", "ΔU% = 400 / ΔU · 100", "Procentní úbytek vztahuješ k síťovému napětí 400 V.", "Vzorce"),
        ("Jak spočítáš příkon motoru, když znáš P2 a η?", "P1 = P2 / η", "P1 = P2·η", "P1 = η / P2", "Příkon je větší než výkon na hřídeli, proto dělíš účinností.", "Vzorce"),
        ("Jak spočítáš současný příkon celé soustavy?", "Pβ = β·ΣP1", "Pβ = ΣP2 / β", "Pβ = β / ΣP1", "Nejdřív sečteš příkony motorů a pak vynásobíš součinitelem současnosti.", "Vzorce"),
        ("Která podmínka musí platit pro proudové vyhovění kabelu?", "dovolený proud kabelu >= jmenovitý proud motoru", "dovolený proud kabelu <= jmenovitý proud motoru", "jmenovitý proud motoru = 0", "Kabel musí zvládnout alespoň proud motoru.", "Vzorce"),
        ("Když používáš ρ v kabelovém vztahu, co to znamená?", "měrný odpor materiálu vodiče", "hustotu kapaliny v potrubí", "počet pólů motoru", "V kabelovém výpočtu je ρ elektrická vlastnost vodiče.", "Vzorce"),
    ]
    for item in formula_questions:
        add(*item)

    selection_questions = [
        ("Motor s otáčkami kolem 2900 ot/min bývá většinou:", "2pólový", "4pólový", "6pólový", "Vyšší otáčky odpovídají menšímu počtu pólů.", "Výběr"),
        ("Motor s otáčkami kolem 1450 ot/min bývá většinou:", "4pólový", "2pólový", "6pólový", "Střední běžné otáčky ukazují na 4 póly.", "Výběr"),
        ("Motor s otáčkami kolem 950 ot/min bývá většinou:", "6pólový", "4pólový", "2pólový", "Nižší otáčky ukazují na vyšší počet pólů.", "Výběr"),
        ("Co rozhoduje o počtu pólů motoru v těchto úlohách nejvíc?", "požadované otáčky", "délka kabelu", "barva vodičů", "Počet pólů souvisí s otáčkami motoru.", "Výběr"),
        ("Kde hledáš účinnost, účiník a jmenovitý proud konkrétního motoru?", "v katalogu/tabulce motorů", "v tabulce vodičů", "v přehledu jističů", "Tyto údaje patří přímo ke konkrétnímu motoru.", "Výběr"),
        ("Kde hledáš dovolený zatěžovací proud kabelu?", "v tabulce proudové zatížitelnosti vodičů", "v katalogu motorů", "v tabulce otáček motorů", "Dovolený proud je vlastnost vedení, ne motoru.", "Výběr"),
        ("Kde hledáš běžné jmenovité hodnoty jističů?", "v přehledu nebo tabulce jističů", "v katalogu čerpadel", "v převodní tabulce litrů", "Jistič vybíráš z jeho normalizované řady.", "Výběr"),
        ("Které síťové napětí dosazuješ do vzorce proudu pro třífázový motor?", "400 V", "230 V", "24 V", "Ve vzorci je sdružené napětí třífázové sítě.", "Výběr"),
        ("Který způsob uložení bývá v těchto úlohách typicky při kabelu na stěně?", "C", "D", "E", "Na stěně se běžně bere uložení C.", "Výběr"),
        ("Který způsob uložení bývá typicky při kabelu v zemi nebo v trubce v zemi?", "D", "C", "A", "V zemi bývá obvykle uložení D.", "Výběr"),
    ]
    for item in selection_questions:
        add(*item)

    mistake_questions = [
        ("Jaká chyba je u čerpadla nejčastější?", "zapomenout převést l/s na m³/s", "zapomenout přepsat počet pólů", "počítat jistič před motorem", "Když Q nepřevedeš, hydraulický výkon vyjde úplně jinak.", "Chyby"),
        ("Jaká chyba je častá u účinnosti η?", "dosadit 70 místo 0,70", "dosadit 0,70 místo 70", "η úplně ignorovat u motoru", "Procenta musíš převést na desetinné číslo.", "Chyby"),
        ("Jaká chyba je častá při výběru motoru?", "vzít menší motor než vyžaduje výpočet", "vzít vyšší standardní výkon", "zkontrolovat i otáčky", "Motor nesmí být slabší než vypočtený požadavek.", "Chyby"),
        ("Jaká chyba je častá u kabelu?", "zkontrolovat jen proud a zapomenout na ΔU", "použít větší průřez", "vzít data z katalogu motoru", "Kabel musí projít dvěma podmínkami, ne jednou.", "Chyby"),
        ("Co musíš udělat po zvětšení průřezu kabelu?", "znovu spočítat odpor a úbytek napětí", "zmenšit výkon motoru", "přepsat počet pólů", "Změnou průřezu se mění odpor vedení.", "Chyby"),
        ("Jaká chyba je častá u vzorce na proud motoru?", "použít 230 V místo 400 V", "použít 400 V místo 230 V u jednofázové lampy", "použít délku kabelu místo napětí", "V těchto úlohách řešíš třífázový motor.", "Chyby"),
        ("Co je špatně na tvrzení 'P1 je menší než P2'?", "je to obráceně, P1 bývá větší než P2", "je to správně vždy", "platí to jen pro čerpadlo", "Na ztráty padne část energie, proto je příkon větší než výkon na hřídeli.", "Chyby"),
        ("Proč není správné zaměnit jmenovitý proud motoru a dovolený proud kabelu?", "jeden patří motoru a druhý kabelu", "obě veličiny znamenají totéž", "dovolený proud kabelu je účinnost motoru", "Jedna hodnota popisuje motor, druhá vedení.", "Chyby"),
        ("Jaká chyba je častá u značky ρ?", "zamění se hustota kapaliny a měrný odpor vodiče", "zamění se napětí a proud", "zamění se póly a otáčky", "Stejný symbol má v různých vztazích jiný význam.", "Chyby"),
        ("Jaká charakteristika jističe je pro motor obvykle špatná první volba?", "B", "C", "D", "Pro běžné motorové úlohy se většinou volí C, ne B.", "Chyby"),
    ]
    for item in mistake_questions:
        add(*item)

    for value in [5, 10, 15, 20, 25]:
        add(
            f"Kolik je {value} l/s v m³/s?",
            f"{format_num(value / 1000, 3)} m³/s",
            f"{format_num(value / 100, 2)} m³/s",
            f"{format_num(value / 10000, 4)} m³/s",
            "Průtok v litrech za sekundu převedeš dělením tisícem.",
            "Převody",
        )

    for value in [60, 70, 75, 80, 85]:
        add(
            f"Kolik je {value} % v desetinném tvaru?",
            format_num(value / 100, 2),
            format_num(value / 10, 1),
            format_num(value / 1000, 3),
            "Procenta ve vzorcích používáš jako desetinné číslo.",
            "Převody",
        )

    for value in [1.5, 2.2, 4.0, 5.5, 7.5]:
        add(
            f"Kolik je {format_num(value,1)} kW ve wattech?",
            f"{int(value * 1000)} W",
            f"{int(value * 100)} W",
            f"{int(value * 10000)} W",
            "Kilowatty převádíš na watty násobením tisícem.",
            "Převody",
        )

    numeric_questions = [
        ("Jaký výkon vyjde pro pilu při F = 150 N a v = 20 m/s?", "3,0 kW", "30,0 kW", "0,3 kW", "P = F·v = 150·20 = 3000 W = 3,0 kW.", "Výpočty"),
        ("Jaké otáčky vyjdou přibližně pro kotouč d = 0,4 m a v = 30 m/s?", "1430 ot/min", "2860 ot/min", "715 ot/min", "n = 60·v/(π·d) vyjde přibližně 1430 ot/min.", "Výpočty"),
        ("Jaký hydraulický výkon vyjde pro Q = 10 l/s a H = 10 m?", "0,98 kW", "9,81 kW", "0,10 kW", "Po převodu Q = 0,01 m³/s vyjde P_h ≈ 0,981 kW.", "Výpočty"),
        ("Jaký výkon motoru vyjde, když P_h = 3,0 kW a η = 75 %?", "4,0 kW", "2,25 kW", "3,75 kW", "P₂ = P_h/η = 3,0/0,75 = 4,0 kW.", "Výpočty"),
        ("Jaký výkon motoru vyjde pro kompresor, když P_k = 4,8 kW a η = 60 %?", "8,0 kW", "2,88 kW", "5,4 kW", "P₂ = 4,8/0,60 = 8,0 kW.", "Výpočty"),
        ("Když má ventilátor P_v = 2,2 kW, jaký potřebný výkon motoru v téhle úloze bereš?", "2,2 kW", "1,1 kW", "3,7 kW", "U ventilátoru se výkon většinou bere přímo ze zadání.", "Výpočty"),
        ("Jaký odpor vyjde pro kabel l = 50 m a S = 2,5 mm²?", "0,35 Ω", "3,5 Ω", "0,035 Ω", "R = 0,0175·50/2,5 = 0,35 Ω.", "Výpočty"),
        ("Jaký příkon P1 vyjde pro motor s P2 = 4,0 kW a η = 0,80?", "5,0 kW", "3,2 kW", "4,8 kW", "P₁ = P₂/η = 4,0/0,80 = 5,0 kW.", "Výpočty"),
        ("Jaký současný příkon vyjde pro ΣP1 = 20 kW a β = 0,6?", "12,0 kW", "33,3 kW", "8,0 kW", "Pβ = 0,6·20 = 12,0 kW.", "Výpočty"),
        ("Když pro kabel 2,5 mm² a uložení C vyjde v tabulce 5 proud jističe 16 A, jaký jistič napíšeš pro motor?", "C16", "C10", "D16", "Proud 16 A vezmeš z tabulky 5 a z tabulky 6 k němu přiřadíš charakteristiku C.", "Výpočty"),
    ]
    for item in numeric_questions:
        add(*item)

    return questions


ABC_BANK = generate_practical_abc_questions()


GUIDE_PDF_NAME = "motor postup.pdf"
TABLES_PDF_NAMES = ["maturita tabulky.pdf", "maturita tabulky (1).pdf"]
REFERENCE_FILES = [GUIDE_PDF_NAME, *TABLES_PDF_NAMES]
TEST_IMAGE_FILES = ["1.png", "2.png"]
DEVICE_ORDER = [
    ("saw", "Pila"),
    ("pump", "Čerpadlo"),
    ("compressor", "Kompresor"),
    ("fan", "Ventilátor"),
]
TEST_FIELD_DEFS = [
    {"key": "motor_kw", "label": "Motor P₂ [kW]", "kind": "number", "tol": 0.06, "digits": 1, "getter": lambda item: item["motor"].power_kw},
    {"key": "poles", "label": "Počet pólů", "kind": "int", "tol": 0.0, "digits": 0, "getter": lambda item: item["motor"].poles},
    {"key": "current_a", "label": "Jmenovitý proud Iₙ [A]", "kind": "number", "tol": 0.25, "digits": 1, "getter": lambda item: item["motor"].current},
    {"key": "section", "label": "Průřez kabelu [mm²]", "kind": "section", "tol": 0.01, "digits": 1, "getter": lambda item: item["section"]},
    {"key": "breaker", "label": "Jistič", "kind": "breaker", "tol": 0.0, "digits": 0, "getter": lambda item: item["breaker"]},
    {"key": "drop_pct", "label": "Úbytek napětí ΔU [%]", "kind": "number", "tol": 0.2, "digits": 2, "getter": lambda item: item["drop_pct"]},
]
FINAL_FIELD_DEF = {"key": "simultaneous_kw", "label": "Současný příkon Pβ [kW]", "kind": "number", "tol": 0.25, "digits": 2}
BASE_WIDTH = 1180
BASE_HEIGHT = 860
NOTES_WIDTH = 360
DOCS_WIDTH = 920
CALC_HEIGHT = 260
TEST_DATA_VERSION = 4


def default_state() -> dict:
    return {
        "test_data_version": TEST_DATA_VERSION,
        "abc": {"best_correct": 0, "best_total": len(ABC_BANK), "last_correct": 0, "last_total": 0},
        "tests": {},
    }


def load_state() -> dict:
    state = default_state()
    if not STATE_FILE.exists():
        return state
    try:
        loaded = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return state
    if isinstance(loaded, dict):
        state["abc"].update(loaded.get("abc", {}))
        loaded_version = loaded.get("test_data_version", 1)
        tests = loaded.get("tests", {})
        if isinstance(tests, dict) and loaded_version == TEST_DATA_VERSION:
            state["tests"] = tests
    state["abc"]["best_total"] = len(ABC_BANK)
    state["abc"]["last_total"] = min(state["abc"].get("last_total", 0), len(ABC_BANK))
    state["abc"]["best_correct"] = min(state["abc"].get("best_correct", 0), len(ABC_BANK))
    state["abc"]["last_correct"] = min(state["abc"].get("last_correct", 0), len(ABC_BANK))
    return state


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def ensure_test_bucket(state: dict, test_id: int) -> dict:
    return state.setdefault("tests", {}).setdefault(
        str(test_id),
        {"completed": False, "best_score": 0, "total": len(TEST_FIELD_DEFS) * len(DEVICE_ORDER) + 1, "answers": {}},
    )


def extract_number(text: str) -> float | None:
    cleaned = text.strip().lower().replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else None


def normalize_code(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def format_expected(field: dict, expected) -> str:
    if field["kind"] == "int":
        return str(int(expected))
    if field["kind"] == "breaker":
        return str(expected)
    if field["kind"] == "section":
        return format_section(float(expected))
    return format_num(float(expected), field.get("digits", 1))


def check_field_answer(field: dict, raw_value: str, expected) -> tuple[bool, str]:
    expected_text = format_expected(field, expected)
    if field["kind"] == "breaker":
        user = normalize_code(raw_value)
        target = normalize_code(str(expected))
        return user in {target, target + "a"}, expected_text
    if field["kind"] == "int":
        value = extract_number(raw_value)
        return value is not None and int(round(value)) == int(expected), expected_text
    value = extract_number(raw_value)
    if value is None:
        return False, expected_text
    return abs(value - float(expected)) <= field.get("tol", 0.1), expected_text


def cable_trials(current_a: float, installation: str, length_m: float, cosphi: float) -> list[dict]:
    trials = []
    for section in SECTIONS:
        ampacity = CABLE_AMPACITY[installation][section]
        protection_limit = protection_current_for_section(installation, section)
        resistance = cable_resistance(length_m, section)
        _, drop_pct = voltage_drop(current_a, resistance, cosphi)
        trials.append(
            {
                "section": section,
                "ampacity": ampacity,
                "protection_limit": protection_limit,
                "resistance": resistance,
                "drop_pct": drop_pct,
                "ok_current": ampacity >= current_a,
                "ok_protection": protection_limit >= current_a,
                "ok_drop": drop_pct <= 5.0,
                "ok": ampacity >= current_a and protection_limit >= current_a and drop_pct <= 5.0,
            }
        )
    return trials


def build_abc_reason(question: ABCQuestion) -> str:
    correct = question.options[question.correct_index]
    wrongs = [option for idx, option in enumerate(question.options) if idx != question.correct_index]
    lines = [
        f"Správně je: {correct}",
        "",
        question.explanation,
        "",
        "Proč ostatní ne:",
    ]
    for wrong in wrongs:
        lines.append(f"- {wrong}: neodpovídá tomu, co se v tomhle kroku nebo pojmu skutečně používá.")
    return prettify_symbols("\n".join(lines))


def load_reference_documents() -> dict[str, dict]:
    documents: dict[str, dict] = {}
    for filename in REFERENCE_FILES:
        path = bundle_dir() / filename
        if not path.exists():
            continue
        page_texts: list[str] = []
        error = ""
        try:
            if PdfReader is not None:
                reader = PdfReader(str(path))
                for page in reader.pages:
                    text = (page.extract_text() or "").strip()
                    page_texts.append(prettify_symbols(text))
        except Exception as exc:
            error = str(exc)
        documents[filename] = {"path": path, "page_texts": page_texts, "page_count": len(page_texts), "error": error}
    if not documents:
        return {"Bez podkladů": {"path": None, "page_texts": [], "page_count": 0, "error": "Vedle aplikace nebyly nalezeny žádné PDF podklady."}}
    ordered: dict[str, dict] = {}
    for name in REFERENCE_FILES:
        if name in documents:
            ordered[name] = documents[name]
    return ordered


def render_pdf_pages(path: Path, target_width: int = 860) -> list[ImageTk.PhotoImage]:
    if pdfium is None or Image is None or ImageTk is None or not path.exists():
        return []
    images: list[ImageTk.PhotoImage] = []
    pdf = pdfium.PdfDocument(str(path))
    try:
        for page_index in range(len(pdf)):
            page = pdf[page_index]
            try:
                page_width = max(page.get_width(), 1.0)
                scale = max(1.4, target_width / page_width)
                pil_image = page.render(scale=scale).to_pil()
                if pil_image.width > target_width:
                    ratio = target_width / pil_image.width
                    pil_image = pil_image.resize((target_width, max(1, int(pil_image.height * ratio))), Image.LANCZOS)
                images.append(ImageTk.PhotoImage(pil_image))
            finally:
                page.close()
    finally:
        pdf.close()
    return images


def load_photo(path: Path, max_size: tuple[int, int]) -> ImageTk.PhotoImage | None:
    if Image is None or ImageTk is None or not path.exists():
        return None
    image = Image.open(path)
    image.thumbnail(max_size)
    return ImageTk.PhotoImage(image)


def build_cable_lines(length_m: float, installation: str, motor: MotorSpec, chosen_section: float, breaker: str) -> list[str]:
    lines = [
        "4) Kabel krok po kroku:",
        f"   Písmeno {installation} bereš z tab. 2 jako uložení kabelu. V tab. 5 pak pro každé uložení a průřez rovnou čteš jmenovitý proud jističe. Nakonec k tomu přiřadíš charakteristiku C.",
        f"   Kabel musí splnit tři podmínky: dovolený proud kabelu >= I_n = {format_num(motor.current,2)} A, proud jističe z tab. 5 musí být aspoň {format_num(motor.current,2)} A a ΔU <= 5 %.",
        "   Vzorce: R = ρ·l/S, ΔU = √3·I·R·cosφ, ΔU % = (√3·I·R·cosφ) / 400 · 100.",
    ]
    for trial in cable_trials(motor.current, installation, length_m, motor.cosphi):
        state = "vyhoví" if trial["ok"] else "nevyhoví"
        reasons = []
        if not trial["ok_current"]:
            reasons.append(f"dovolený proud kabelu {format_num(trial['ampacity'],1)} A je menší než I_n")
        if not trial["ok_protection"]:
            reasons.append(f"tab. 5 pro {format_section(trial['section'])} a uložení {installation} dává jen {int(trial['protection_limit'])} A, což je méně než I_n")
        protection_text = f"{int(trial['protection_limit'])} A"
        if not trial["ok_drop"]:
            reasons.append(f"ΔU = {format_num(trial['drop_pct'],2)} % je nad limitem 5 %")
        reason_text = " a ".join(reasons) if reasons else f"splní proud, tabulku 5 i úbytek; pro tenhle kabel by z tab. 5 vyšel jistič {int(trial['protection_limit'])} A"
        lines.append(
            f"   {format_section(trial['section'])}: dovolený proud kabelu = {format_num(trial['ampacity'],1)} A, tab. 5 dovolí jistící prvek {protection_text}, "
            f"R = {format_num(trial['resistance'],3)} Ω, ΔU % = (√3·{format_num(motor.current,2)}·{format_num(trial['resistance'],3)}·{format_num(motor.cosphi,2)}) / 400 · 100 = {format_num(trial['drop_pct'],2)} % -> {state}, protože {reason_text}."
        )
        if trial["section"] == chosen_section:
            break
    lines.append(f"   Beru {format_section(chosen_section)}, protože je to první nejmenší průřez, který projde proudem, tabulkou 5 i úbytkem. Pro tenhle kabel pak z tab. 5 vyjde proud jističe {protection_current_for_section(installation, chosen_section)} A, takže jistič je {breaker}.")
    return lines


def build_device_solution(device_key: str, scenario: dict, solved: dict) -> list[str]:
    motor = solved["motor"]
    p1_kw = motor.power_kw / motor.eta
    label = dict(DEVICE_ORDER)[device_key].upper()
    lines = [label, f"Zadání: {solved['task_text']}"]

    if device_key == "saw":
        mechanical_w = scenario["force_n"] * scenario["speed_ms"]
        lines.extend(
            [
                "1) Výkon na hřídeli P2:",
                f"   P2 = F·v = {format_num(scenario['force_n'],0)} · {format_num(scenario['speed_ms'],0)} = {format_num(mechanical_w,0)} W = {format_num(solved['required_kw'],2)} kW.",
                "2) Požadované otáčky kotouče:",
                f"   n = 60·v / (π·d) = 60·{format_num(scenario['speed_ms'],0)} / (π·{format_num(scenario['diameter_m'],2)}) = {format_num(solved['rpm'],0)} ot/min.",
            ]
        )
    elif device_key == "pump":
        flow_m3s = scenario["flow_lps"] / 1000
        lines.extend(
            [
                "1) Převod průtoku:",
                f"   Q = {format_num(scenario['flow_lps'],0)} l/s = {format_num(flow_m3s,3)} m³/s.",
                "2) Hydraulický výkon:",
                f"   P_h = ρ·g·Q·H = 1000·9,81·{format_num(flow_m3s,3)}·{format_num(scenario['head_m'],0)} = {format_num(solved['hydraulic_kw'],2)} kW.",
                "3) Potřebný výkon motoru:",
                f"   P2 = P_h / η = {format_num(solved['hydraulic_kw'],2)} / {format_num(scenario['task_eta'],2)} = {format_num(solved['required_kw'],2)} kW.",
            ]
        )
    elif device_key == "compressor":
        lines.extend(
            [
                "1) Potřebný výkon motoru:",
                f"   P2 = P_k / η = {format_num(scenario['pk_kw'],2)} / {format_num(scenario['task_eta'],2)} = {format_num(solved['required_kw'],2)} kW.",
                "2) Otáčky motoru bereš přímo ze zadání:",
                f"   n ≈ {format_num(solved['rpm'],0)} ot/min.",
            ]
        )
    else:
        lines.extend(
            [
                "1) Potřebný výkon motoru:",
                f"   P2 = P_v = {format_num(scenario['pv_kw'],2)} kW.",
                "2) Otáčky motoru bereš přímo ze zadání:",
                f"   n ≈ {format_num(solved['rpm'],0)} ot/min.",
            ]
        )

    lines.extend(
        [
            "3) Výběr motoru z tabulky 1:",
            f"   Hledám první vyšší standardní výkon než {format_num(solved['required_kw'],2)} kW a podle otáček beru {motor.poles}-pólový řádek.",
            f"   Vybraný motor: {format_num(motor.power_kw,1)} kW, {motor.poles} póly, n = {format_num(motor.rpm,0)} ot/min, η = {format_num(motor.eta,3)}, cosφ = {format_num(motor.cosphi,2)}, I_n = {format_num(motor.current,2)} A.",
        ]
    )
    lines.extend(build_cable_lines(scenario["length_m"], scenario["installation"], motor, solved["section"], solved["breaker"]))
    lines.extend(
        [
            "5) Jistič:",
            f"   Z tab. 5 pro vybraný kabel a uložení vyjde proud jističe {solved['breaker'][1:]} A. K tomu přiřadím pro motor charakteristiku C -> {solved['breaker']}.",
            "6) Příkon motoru pro soudobost:",
            f"   P1 = P2 / η = {format_num(motor.power_kw,1)} / {format_num(motor.eta,3)} = {format_num(p1_kw,2)} kW.",
            "7) Výsledek do závěru:",
            f"   Motor {format_num(motor.power_kw,1)} kW, {motor.poles} póly, I_n {format_num(motor.current,1)} A, kabel {format_section(solved['section'])}, jistič {solved['breaker']}, ΔU {format_num(solved['drop_pct'],2)} %.",
        ]
    )
    return lines


def build_test_solution_text(test: TestScenario, solved: dict, results: list[dict] | None = None) -> str:
    lines: list[str] = []
    if results is not None:
        wrong = [item for item in results if not item["ok"]]
        if wrong:
            lines.append("KDE MÁŠ CHYBY")
            for item in wrong:
                user = item["user"] if item["user"] else "(prázdné pole)"
                lines.append(
                    f"- {item['device_label']} | {item['field_label']}: napsal jsi {user}, správně je {item['expected']}."
                )
        else:
            lines.append("VŠECHNO JE SPRÁVNĚ")
            lines.append("Všechna pole vyšla správně. Níž máš celý správný postup.")
        lines.append("")

    lines.append(test.title.upper())
    lines.append(f"β = {format_num(test.beta,2)}")
    lines.append("")
    for device_key, _ in DEVICE_ORDER:
        scenario = getattr(test, device_key)
        lines.extend(build_device_solution(device_key, scenario, solved[device_key]))
        lines.append("")

    p1_values = []
    lines.append("SOUČASNÝ PŘÍKON")
    for device_key, label in DEVICE_ORDER:
        motor = solved[device_key]["motor"]
        p1_kw = motor.power_kw / motor.eta
        p1_values.append(p1_kw)
        lines.append(
            f"{label}: P1 = {format_num(motor.power_kw,1)} / {format_num(motor.eta,3)} = {format_num(p1_kw,2)} kW."
        )
    lines.append(f"ΣP1 = {format_num(sum(p1_values),2)} kW.")
    lines.append(
        f"Pβ = β·ΣP1 = {format_num(test.beta,2)} · {format_num(sum(p1_values),2)} = {format_num(solved['simultaneous_kw'],2)} kW."
    )
    lines.append("")
    lines.append("KONEČNÝ ZÁVĚR")
    for device_key, label in DEVICE_ORDER:
        item = solved[device_key]
        lines.append(
            f"{label}: motor {format_num(item['motor'].power_kw,1)} kW, {item['motor'].poles} póly, kabel {format_section(item['section'])}, "
            f"jistič {item['breaker']}, ΔU {format_num(item['drop_pct'],2)} %."
        )
    lines.append(f"Celý soustavný/současný příkon: Pβ = {format_num(solved['simultaneous_kw'],2)} kW.")
    return prettify_symbols("\n".join(lines))


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg: str = BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_inner_configure(self, _event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event) -> None:
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event) -> None:
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event) -> None:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class MotorQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.progress_state = load_state()
        self.reference_docs: dict[str, dict] = {}
        self.doc_image_cache: dict[str, list[ImageTk.PhotoImage]] = {}
        self.doc_page_frames: list[tk.Frame] = []
        self.doc_page_positions: list[int] = []
        self.reference_loaded = False
        self.doc_matches: list[int] = []
        self.doc_match_index = 0
        self.doc_last_term = ""
        self.notes_visible = False
        self.docs_visible = False
        self.calc_visible = False
        self.notes_tool = "pen"
        self.last_note_point: tuple[int, int] | None = None
        self.calc_last_result = 0.0
        self.photo_refs: list[ImageTk.PhotoImage] = []
        self.current_test_id: int | None = None
        self.current_test_entries: dict[tuple[str, str], tk.Entry] = {}
        self.current_test_results: list[dict] = []
        self.current_test_explanation_shown = False
        self.abc_questions = ABC_BANK[:]
        self.abc_index = 0
        self.abc_correct = 0
        self.abc_answered = 0
        self.abc_selected: int | None = None

        self.doc_var = tk.StringVar(value=REFERENCE_FILES[0])
        self.doc_search_var = tk.StringVar(value="")
        self.doc_status_var = tk.StringVar(value="Vyber PDF a můžeš scrollovat nebo hledat.")
        self.calc_var = tk.StringVar(value="")
        self.calc_status_var = tk.StringVar(value="Kalkulačka připravená.")
        self.notes_window: tk.Toplevel | None = None
        self.docs_window: tk.Toplevel | None = None
        self.calc_window: tk.Toplevel | None = None

        self.title(APP_TITLE)
        self.configure(bg=BG)
        self.geometry(f"{BASE_WIDTH}x{BASE_HEIGHT}")
        self.minsize(1060, 760)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        try:
            if ICON_FILE.exists():
                self.iconbitmap(str(ICON_FILE))
        except Exception:
            pass

        self._build_shell()
        self.show_home()

    def _build_shell(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        topbar = tk.Frame(self, bg=NAVY, padx=18, pady=14)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_columnconfigure(0, weight=1)
        tk.Label(topbar, text="Motor Quiz", bg=NAVY, fg="white", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")

        nav = tk.Frame(topbar, bg=NAVY)
        nav.grid(row=0, column=1, sticky="e")
        self._make_nav_button(nav, "Domů", self.show_home).pack(side="left", padx=4)
        self._make_nav_button(nav, "ABC", self.start_abc).pack(side="left", padx=4)
        self._make_nav_button(nav, "Test", self.show_test_list).pack(side="left", padx=4)
        self._make_nav_button(nav, "Postup", self.show_guide_pdf).pack(side="left", padx=4)
        self._make_nav_button(nav, "Tabulky", self.show_tables_pdf).pack(side="left", padx=4)
        self._make_nav_button(nav, "Zápisky", self.toggle_notes_panel).pack(side="left", padx=4)
        self._make_nav_button(nav, "Kalkulačka", self.toggle_calc_panel).pack(side="left", padx=4)

        self.workspace = tk.Frame(self, bg=BG)
        self.workspace.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.workspace.grid_rowconfigure(0, weight=1)
        self.workspace.grid_columnconfigure(0, weight=1)

        self.center = tk.Frame(self.workspace, bg=BG)
        self.center.grid(row=0, column=0, sticky="nsew")

        self.notes_window = tk.Toplevel(self)
        self.notes_window.withdraw()
        self.notes_window.title("Motor Quiz | Zápisky")
        self.notes_window.configure(bg=BG)
        self.notes_window.geometry(f"{NOTES_WIDTH}x{BASE_HEIGHT}")
        self.notes_window.minsize(320, 500)
        self.notes_window.protocol("WM_DELETE_WINDOW", self._hide_notes_window)
        try:
            if ICON_FILE.exists():
                self.notes_window.iconbitmap(str(ICON_FILE))
        except Exception:
            pass
        self.notes_panel = tk.Frame(self.notes_window, bg=CARD, highlightbackground=LINE, highlightthickness=1)
        self.notes_panel.pack(fill="both", expand=True, padx=12, pady=12)

        self.docs_window = tk.Toplevel(self)
        self.docs_window.withdraw()
        self.docs_window.title("Motor Quiz | Tabulky a guide")
        self.docs_window.configure(bg=BG)
        self.docs_window.geometry(f"{DOCS_WIDTH}x{BASE_HEIGHT}")
        self.docs_window.minsize(820, 700)
        self.docs_window.protocol("WM_DELETE_WINDOW", self._hide_docs_window)
        try:
            if ICON_FILE.exists():
                self.docs_window.iconbitmap(str(ICON_FILE))
        except Exception:
            pass
        self.docs_panel = tk.Frame(self.docs_window, bg=CARD, highlightbackground=LINE, highlightthickness=1)
        self.docs_panel.pack(fill="both", expand=True, padx=12, pady=12)

        self.calc_window = tk.Toplevel(self)
        self.calc_window.withdraw()
        self.calc_window.title("Motor Quiz | Kalkulačka")
        self.calc_window.configure(bg=BG)
        self.calc_window.geometry(f"520x{CALC_HEIGHT}")
        self.calc_window.minsize(420, 260)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._hide_calc_window)
        try:
            if ICON_FILE.exists():
                self.calc_window.iconbitmap(str(ICON_FILE))
        except Exception:
            pass
        self.calc_panel = tk.Frame(self.calc_window, bg=CARD, highlightbackground=LINE, highlightthickness=1)
        self.calc_panel.pack(fill="both", expand=True, padx=12, pady=12)

        self._build_notes_panel()
        self._build_docs_panel()
        self._build_calc_panel()

    def _make_nav_button(self, parent, text: str, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=BLUE,
            fg="white",
            activebackground=TEAL,
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )

    def _clear_center(self) -> None:
        self.photo_refs.clear()
        for child in self.center.winfo_children():
            child.destroy()

    def _update_window_geometry(self) -> None:
        self.geometry(f"{BASE_WIDTH}x{BASE_HEIGHT}")

    def _show_notes_window(self) -> None:
        if self.notes_window is None:
            return
        self.notes_visible = True
        self.update_idletasks()
        x = max(0, self.winfo_rootx() - NOTES_WIDTH - 12)
        y = self.winfo_rooty()
        self.notes_window.geometry(f"{NOTES_WIDTH}x{BASE_HEIGHT}+{x}+{max(0, y)}")
        self.notes_window.deiconify()
        self.notes_window.lift()

    def _hide_notes_window(self) -> None:
        self.notes_visible = False
        if self.notes_window is not None:
            self.notes_window.withdraw()

    def _show_docs_window(self) -> None:
        if self.docs_window is None:
            return
        self.docs_visible = True
        self.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() + 12
        y = self.winfo_rooty()
        max_x = max(0, self.winfo_screenwidth() - DOCS_WIDTH - 20)
        self.docs_window.geometry(f"{DOCS_WIDTH}x{BASE_HEIGHT}+{min(x, max_x)}+{max(0, y)}")
        self.docs_window.deiconify()
        self.docs_window.lift()
        self.docs_window.focus_force()

    def _hide_docs_window(self) -> None:
        self.docs_visible = False
        if self.docs_window is not None:
            self.docs_window.withdraw()

    def _show_calc_window(self) -> None:
        if self.calc_window is None:
            return
        self.calc_visible = True
        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 12
        max_y = max(0, self.winfo_screenheight() - CALC_HEIGHT - 80)
        self.calc_window.geometry(f"520x{CALC_HEIGHT}+{max(0, x)}+{min(y, max_y)}")
        self.calc_window.deiconify()
        self.calc_window.lift()

    def _hide_calc_window(self) -> None:
        self.calc_visible = False
        if self.calc_window is not None:
            self.calc_window.withdraw()

    def toggle_notes_panel(self) -> None:
        if self.notes_visible:
            self._hide_notes_window()
        else:
            self._show_notes_window()

    def toggle_docs_panel(self) -> None:
        if self.docs_visible:
            self._hide_docs_window()
        else:
            self._show_docs_window()
            self.ensure_reference_docs_loaded()

    def show_guide_pdf(self) -> None:
        self._show_docs_window()
        self.ensure_reference_docs_loaded()
        if GUIDE_PDF_NAME in self.reference_docs:
            self.doc_var.set(GUIDE_PDF_NAME)
        else:
            self._render_doc_pdf()

    def show_tables_pdf(self) -> None:
        self._show_docs_window()
        self.ensure_reference_docs_loaded()
        for name in TABLES_PDF_NAMES:
            if name in self.reference_docs:
                self.doc_var.set(name)
                return
        self._render_doc_pdf()

    def toggle_calc_panel(self) -> None:
        if self.calc_visible:
            self._hide_calc_window()
        else:
            self._show_calc_window()

    def _build_notes_panel(self) -> None:
        header = tk.Frame(self.notes_panel, bg=CARD)
        header.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(header, text="Zápisky", bg=CARD, fg=INK, font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Button(header, text="Pero", command=lambda: self._set_notes_tool("pen"), bg=BLUE, fg="white", relief="flat", cursor="hand2").pack(side="left", padx=4)
        tk.Button(header, text="Guma", command=lambda: self._set_notes_tool("eraser"), bg=AMBER, fg="white", relief="flat", cursor="hand2").pack(side="left", padx=4)
        tk.Button(header, text="Smazat", command=self._clear_notes, bg=RED, fg="white", relief="flat", cursor="hand2").pack(side="right")
        self.notes_canvas = tk.Canvas(self.notes_panel, bg="white", highlightthickness=0, cursor="pencil")
        self.notes_canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.notes_canvas.bind("<ButtonPress-1>", self._notes_press)
        self.notes_canvas.bind("<B1-Motion>", self._notes_drag)
        self.notes_canvas.bind("<ButtonRelease-1>", self._notes_release)

    def _set_notes_tool(self, tool: str) -> None:
        self.notes_tool = tool

    def _clear_notes(self) -> None:
        self.notes_canvas.delete("all")

    def _notes_press(self, event) -> None:
        self.last_note_point = (event.x, event.y)

    def _notes_drag(self, event) -> None:
        if self.last_note_point is None:
            self.last_note_point = (event.x, event.y)
            return
        x0, y0 = self.last_note_point
        color = "white" if self.notes_tool == "eraser" else INK
        width = 18 if self.notes_tool == "eraser" else 2
        self.notes_canvas.create_line(x0, y0, event.x, event.y, fill=color, width=width, capstyle="round", smooth=True)
        self.last_note_point = (event.x, event.y)

    def _notes_release(self, _event) -> None:
        self.last_note_point = None

    def _build_docs_panel(self) -> None:
        header = tk.Frame(self.docs_panel, bg=CARD)
        header.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(header, text="Tabulky a guide", bg=CARD, fg=INK, font=("Segoe UI", 13, "bold")).pack(side="left")

        controls = tk.Frame(self.docs_panel, bg=CARD)
        controls.pack(fill="x", padx=12, pady=(0, 8))
        self.doc_option = tk.OptionMenu(controls, self.doc_var, self.doc_var.get())
        self.doc_option.config(bg=BG, fg=INK, relief="flat", highlightthickness=0, activebackground=BG)
        self.doc_option.pack(side="left", fill="x", expand=True)
        self.doc_var.trace_add("write", lambda *_args: self._render_doc_pdf())

        search = tk.Frame(self.docs_panel, bg=CARD)
        search.pack(fill="x", padx=12, pady=(0, 8))
        tk.Entry(search, textvariable=self.doc_search_var, font=("Consolas", 10)).pack(side="left", fill="x", expand=True)
        tk.Button(search, text="Najít", command=self._search_docs, bg=BLUE, fg="white", relief="flat", cursor="hand2").pack(side="left", padx=4)
        tk.Button(search, text="Další", command=lambda: self._search_docs(next_hit=True), bg=TEAL, fg="white", relief="flat", cursor="hand2").pack(side="left")

        tk.Label(self.docs_panel, textvariable=self.doc_status_var, bg=CARD, fg=MUTED, font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=12, pady=(0, 8))

        viewer_wrap = tk.Frame(self.docs_panel, bg=CARD)
        viewer_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.docs_canvas = tk.Canvas(viewer_wrap, bg="#E9EDF3", highlightthickness=0)
        doc_scroll = tk.Scrollbar(viewer_wrap, orient="vertical", command=self.docs_canvas.yview)
        self.docs_canvas.configure(yscrollcommand=doc_scroll.set)
        self.docs_canvas.pack(side="left", fill="both", expand=True)
        doc_scroll.pack(side="right", fill="y")
        self.docs_inner = tk.Frame(self.docs_canvas, bg="#E9EDF3")
        self.docs_window_id = self.docs_canvas.create_window((0, 0), window=self.docs_inner, anchor="nw")
        self.docs_inner.bind("<Configure>", self._on_docs_inner_configure)
        self.docs_canvas.bind("<Configure>", self._on_docs_canvas_configure)
        self.docs_canvas.bind("<Enter>", self._bind_docs_wheel)
        self.docs_canvas.bind("<Leave>", self._unbind_docs_wheel)
        tk.Label(self.docs_inner, text="Klikni na Tabulky nebo Postup a načtou se skutečné stránky PDF.", bg="#E9EDF3", fg=MUTED, font=("Segoe UI", 10)).pack(pady=20)

    def ensure_reference_docs_loaded(self) -> None:
        if self.reference_loaded:
            return
        self.reference_docs = load_reference_documents()
        self.reference_loaded = True
        self._refresh_doc_menu()
        self._render_doc_pdf()

    def _refresh_doc_menu(self) -> None:
        menu = self.doc_option["menu"]
        menu.delete(0, "end")
        names = list(self.reference_docs.keys()) or ["Bez podkladů"]
        for name in names:
            menu.add_command(label=name, command=tk._setit(self.doc_var, name))
        if self.doc_var.get() not in names:
            self.doc_var.set(names[0])

    def _render_doc_pdf(self) -> None:
        current = self.doc_var.get()
        doc = self.reference_docs.get(current)
        self.doc_matches = []
        self.doc_matches = []
        self.doc_match_index = 0
        self.doc_last_term = ""

        for child in self.docs_inner.winfo_children():
            child.destroy()
        self.doc_page_frames = []
        self.doc_page_positions = []

        if not doc or not doc.get("path"):
            self.doc_status_var.set("PDF podklad není dostupný.")
            tk.Label(self.docs_inner, text="PDF podklad není dostupný.", bg="#E9EDF3", fg=RED, font=("Segoe UI", 10, "bold")).pack(pady=20)
            self.docs_canvas.yview_moveto(0)
            return

        path = doc["path"]
        if current not in self.doc_image_cache:
            self.doc_status_var.set(f"Načítám {current}...")
            self.update_idletasks()
            self.doc_image_cache[current] = render_pdf_pages(path, target_width=860)

        images = self.doc_image_cache.get(current, [])
        if not images:
            error_text = "PDF nejde vykreslit. Chybí renderer nebo je soubor poškozený."
            if doc.get("error"):
                error_text += f" Detail: {doc['error']}"
            self.doc_status_var.set(error_text)
            tk.Label(self.docs_inner, text=error_text, bg="#E9EDF3", fg=RED, font=("Segoe UI", 10, "bold"), wraplength=820, justify="left").pack(pady=20, padx=12)
            self.docs_canvas.yview_moveto(0)
            return

        for page_index, image in enumerate(images, start=1):
            frame = tk.Frame(self.docs_inner, bg="#D8DEE9", padx=8, pady=8)
            frame.pack(fill="x", pady=(0, 12))
            tk.Label(frame, text=f"{current} | strana {page_index}/{len(images)}", bg="#D8DEE9", fg=INK, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 6))
            tk.Label(frame, image=image, bg="white").pack()
            self.doc_page_frames.append(frame)

        self.docs_inner.update_idletasks()
        self.docs_canvas.configure(scrollregion=self.docs_canvas.bbox("all"))
        self.doc_page_positions = [frame.winfo_y() for frame in self.doc_page_frames]
        self.docs_canvas.yview_moveto(0)
        self.doc_status_var.set(f"{current} | {len(images)} stran | scrolluj nebo hledej výraz.")

    def _search_docs(self, next_hit: bool = False) -> None:
        term = self.doc_search_var.get().strip()
        if not term:
            self.doc_matches = []
            self.doc_status_var.set("Zadej výraz pro hledání v aktuálním PDF.")
            return
        current = self.doc_var.get()
        doc = self.reference_docs.get(current, {})
        page_texts = doc.get("page_texts", [])
        if not next_hit or term != self.doc_last_term or not self.doc_matches:
            self.doc_last_term = term
            self.doc_matches = []
            lowered = term.lower()
            for page_index, text in enumerate(page_texts):
                if lowered in text.lower():
                    self.doc_matches.append(page_index)
            self.doc_match_index = 0
        elif self.doc_matches:
            self.doc_match_index = (self.doc_match_index + 1) % len(self.doc_matches)
        if not self.doc_matches:
            self.doc_status_var.set(f"V {current} jsem '{term}' nenašel.")
            return
        page_index = self.doc_matches[self.doc_match_index]
        self._scroll_to_doc_page(page_index)
        self.doc_status_var.set(
            f"{current} | nalezeno {len(self.doc_matches)}x | skok na stranu {page_index + 1} ({self.doc_match_index + 1}/{len(self.doc_matches)})."
        )

    def _scroll_to_doc_page(self, page_index: int) -> None:
        if not self.doc_page_positions:
            return
        page_index = max(0, min(page_index, len(self.doc_page_positions) - 1))
        total_height = max(self.docs_inner.winfo_height(), 1)
        y = self.doc_page_positions[page_index] / total_height
        self.docs_canvas.yview_moveto(y)
        for idx, frame in enumerate(self.doc_page_frames):
            frame.configure(bg="#F6D365" if idx == page_index else "#D8DEE9")
            for child in frame.winfo_children():
                child.configure(bg="#F6D365" if idx == page_index else ("white" if isinstance(child, tk.Label) and str(child.cget("image")) else "#D8DEE9"))

    def _on_docs_inner_configure(self, _event) -> None:
        self.docs_canvas.configure(scrollregion=self.docs_canvas.bbox("all"))

    def _on_docs_canvas_configure(self, event) -> None:
        self.docs_canvas.itemconfigure(self.docs_window_id, width=event.width)

    def _bind_docs_wheel(self, _event) -> None:
        self.docs_canvas.bind_all("<MouseWheel>", self._on_docs_wheel)

    def _unbind_docs_wheel(self, _event) -> None:
        self.docs_canvas.unbind_all("<MouseWheel>")

    def _on_docs_wheel(self, event) -> None:
        self.docs_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_calc_panel(self) -> None:
        top = tk.Frame(self.calc_panel, bg=CARD)
        top.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(top, text="Kalkulačka", bg=CARD, fg=INK, font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(top, textvariable=self.calc_status_var, bg=CARD, fg=MUTED, font=("Segoe UI", 10)).pack(side="right")

        display = tk.Entry(self.calc_panel, textvariable=self.calc_var, font=("Consolas", 16), relief="solid", bd=1, justify="right")
        display.pack(fill="x", padx=12, pady=(0, 8))

        keypad = tk.Frame(self.calc_panel, bg=CARD)
        keypad.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        buttons = [
            ["7", "8", "9", "/", "C"],
            ["4", "5", "6", "*", "⌫"],
            ["1", "2", "3", "-", "("],
            ["0", ",", "=", "+", ")"],
            ["sqrt(", "pi", "^", "ANS", "CLS"],
        ]
        for row_index, row in enumerate(buttons):
            keypad.grid_rowconfigure(row_index, weight=1)
            for col_index, token in enumerate(row):
                keypad.grid_columnconfigure(col_index, weight=1)
                command = lambda value=token: self._calc_button(value)
                tk.Button(
                    keypad,
                    text=token,
                    command=command,
                    bg=BG if token not in {"=", "C", "CLS"} else (GREEN if token == "=" else RED),
                    fg=INK if token not in {"=", "C", "CLS"} else "white",
                    relief="flat",
                    font=("Segoe UI", 11, "bold"),
                    cursor="hand2",
                ).grid(row=row_index, column=col_index, sticky="nsew", padx=4, pady=4)

    def _calc_button(self, token: str) -> None:
        if token == "=":
            self._calc_eval()
            return
        if token in {"C", "CLS"}:
            self.calc_var.set("")
            self.calc_status_var.set("Vymazáno.")
            return
        if token == "⌫":
            self.calc_var.set(self.calc_var.get()[:-1])
            return
        if token == "ANS":
            self.calc_var.set(self.calc_var.get() + str(self.calc_last_result).replace(".", ","))
            return
        self.calc_var.set(self.calc_var.get() + token)

    def _calc_eval(self) -> None:
        expr = self.calc_var.get().strip()
        if not expr:
            return
        try:
            clean = expr.replace(",", ".").replace("^", "**").replace("ANS", str(self.calc_last_result)).replace("ans", str(self.calc_last_result))
            tokens = re.findall(r"[A-Za-z_]+", clean)
            if any(token not in {"sqrt", "pi"} for token in tokens):
                raise ValueError("Nepovolený výraz")
            if not re.fullmatch(r"[0-9\.\+\-\*\/\(\)\sA-Za-z_]+", clean):
                raise ValueError("Nepovolený znak")
            result = eval(clean, {"__builtins__": {}}, {"sqrt": math.sqrt, "pi": math.pi})
            self.calc_last_result = float(result)
            self.calc_var.set(str(result).replace(".", ","))
            self.calc_status_var.set("Výpočet hotový.")
        except Exception:
            self.calc_status_var.set("Chyba ve výrazu.")

    def show_home(self) -> None:
        self._clear_center()
        abc_state = self.progress_state.get("abc", {})
        completed = sum(1 for value in self.progress_state.get("tests", {}).values() if value.get("completed"))

        wrap = tk.Frame(self.center, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=24)
        card = tk.Frame(wrap, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=28, pady=28)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Motor guide jako quiz", bg=CARD, fg=NAVY, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(
            card,
            text="Vyber si ABC na dril pojmů, tabulek a vzorců, nebo Test na celé maturitní příklady krok po kroku.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(8, 20))

        stats = tk.Frame(card, bg=CARD)
        stats.pack(fill="x", pady=(0, 24))
        stat_texts = [
            f"ABC naposledy: {abc_state.get('last_correct', 0)}/{abc_state.get('last_total', 0)}",
            f"ABC best: {abc_state.get('best_correct', 0)}/{abc_state.get('best_total', len(ABC_BANK))}",
            f"Hotové testy: {completed}/20",
        ]
        for text in stat_texts:
            tk.Label(stats, text=text, bg=BG, fg=INK, font=("Segoe UI", 11, "bold"), padx=16, pady=12).pack(side="left", padx=(0, 12))

        buttons = tk.Frame(card, bg=CARD)
        buttons.pack(fill="both", expand=True)
        self._make_main_button(
            buttons,
            "ABC",
            f"{len(ABC_BANK)} kvalitních obecných otázek na značky, vzorce, postup, převody a chyby.",
            self.start_abc,
            BLUE,
        ).pack(fill="x", pady=10)
        self._make_main_button(
            buttons,
            "TEST",
            "20 maturitních zadání s vlastními odpověďmi, vyhodnocením a plným správným postupem.",
            self.show_test_list,
            TEAL,
        ).pack(fill="x", pady=10)

        tk.Label(
            card,
            text="Boční tlačítka Tabulky, Zápisky a Kalkulačka můžeš zapnout i během řešení testu.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(16, 0))

    def _make_main_button(self, parent, title: str, subtitle: str, command, color: str):
        frame = tk.Frame(parent, bg=color, cursor="hand2")
        button = tk.Button(
            frame,
            text=f"{title}\n{subtitle}",
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            justify="left",
            anchor="w",
            padx=22,
            pady=22,
            font=("Segoe UI", 16, "bold"),
            cursor="hand2",
            wraplength=880,
        )
        button.pack(fill="x")
        return frame

    def start_abc(self) -> None:
        self.abc_questions = random.sample(ABC_BANK, k=len(ABC_BANK))
        self.abc_index = 0
        self.abc_correct = 0
        self.abc_answered = 0
        self.abc_selected = None
        self._render_abc_question()

    def _render_abc_question(self) -> None:
        if self.abc_index >= len(self.abc_questions):
            self._render_abc_summary()
            return

        question = self.abc_questions[self.abc_index]
        self.abc_selected = None
        self.abc_reason_visible = False
        self._clear_center()

        wrap = tk.Frame(self.center, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=24)
        card = tk.Frame(wrap, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=28, pady=28)
        card.pack(fill="both", expand=True)

        top = tk.Frame(card, bg=CARD)
        top.pack(fill="x")
        self.abc_score_label = tk.Label(
            top,
            text=f"Skóre {self.abc_correct}/{self.abc_answered}",
            bg=BG,
            fg=INK,
            font=("Segoe UI", 11, "bold"),
            padx=14,
            pady=10,
        )
        self.abc_score_label.pack(side="left")
        tk.Label(
            top,
            text=f"Otázka {self.abc_index + 1}/{len(self.abc_questions)} | {question.category}",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(side="right")

        tk.Label(
            card,
            text=question.prompt,
            bg=CARD,
            fg=NAVY,
            font=("Segoe UI", 22, "bold"),
            wraplength=880,
            justify="center",
        ).pack(fill="x", pady=(26, 28))

        options_wrap = tk.Frame(card, bg=CARD)
        options_wrap.pack(fill="x")
        self.abc_option_buttons = []
        for index, option in enumerate(question.options):
            button = tk.Button(
                options_wrap,
                text=option,
                command=lambda idx=index: self._answer_abc(idx),
                bg=BG,
                fg=INK,
                activebackground=BG,
                activeforeground=INK,
                relief="flat",
                wraplength=860,
                justify="left",
                anchor="w",
                padx=18,
                pady=16,
                font=("Segoe UI", 13, "bold"),
                cursor="hand2",
            )
            button.pack(fill="x", pady=8)
            self.abc_option_buttons.append(button)

        controls = tk.Frame(card, bg=CARD)
        controls.pack(fill="x", pady=(18, 0))
        self.abc_reason_button = tk.Button(
            controls,
            text="Důvod",
            command=self._toggle_abc_reason,
            state="disabled",
            bg=AMBER,
            fg="white",
            relief="flat",
            padx=16,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
        )
        self.abc_reason_button.pack(side="left")
        self.abc_next_button = tk.Button(
            controls,
            text="Výsledky" if self.abc_index == len(self.abc_questions) - 1 else "Další",
            command=self._next_abc,
            state="disabled",
            bg=GREEN,
            fg="white",
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
        )
        self.abc_next_button.pack(side="right")

        self.abc_reason_box = tk.Label(
            card,
            text=build_abc_reason(question),
            bg="#FFF8E1",
            fg=INK,
            font=("Consolas", 10),
            justify="left",
            anchor="w",
            wraplength=880,
            padx=16,
            pady=14,
        )

    def _answer_abc(self, index: int) -> None:
        if self.abc_selected is not None:
            return
        question = self.abc_questions[self.abc_index]
        self.abc_selected = index
        self.abc_answered += 1
        if index == question.correct_index:
            self.abc_correct += 1
        for option_index, button in enumerate(self.abc_option_buttons):
            if option_index == question.correct_index:
                button.configure(bg=GREEN, fg="white", activebackground=GREEN, activeforeground="white")
            elif option_index == index:
                button.configure(bg=RED, fg="white", activebackground=RED, activeforeground="white")
            else:
                button.configure(bg=BG, fg=INK, activebackground=BG, activeforeground=INK)
            button.configure(state="disabled")
        self.abc_score_label.configure(text=f"Skóre {self.abc_correct}/{self.abc_answered}")
        self.abc_reason_button.configure(state="normal")
        self.abc_next_button.configure(state="normal")

    def _toggle_abc_reason(self) -> None:
        if self.abc_selected is None:
            return
        if self.abc_reason_visible:
            self.abc_reason_box.pack_forget()
            self.abc_reason_visible = False
        else:
            self.abc_reason_box.pack(fill="x", pady=(18, 0))
            self.abc_reason_visible = True

    def _next_abc(self) -> None:
        if self.abc_selected is None:
            return
        self.abc_index += 1
        self._render_abc_question()

    def _render_abc_summary(self) -> None:
        abc_state = self.progress_state.setdefault("abc", default_state()["abc"])
        abc_state["last_correct"] = self.abc_correct
        abc_state["last_total"] = len(self.abc_questions)
        if self.abc_correct >= abc_state.get("best_correct", 0):
            abc_state["best_correct"] = self.abc_correct
            abc_state["best_total"] = len(self.abc_questions)
        save_state(self.progress_state)

        percent = 100 * self.abc_correct / max(1, len(self.abc_questions))
        self._clear_center()
        wrap = tk.Frame(self.center, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=24)
        card = tk.Frame(wrap, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=28, pady=28)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Výsledky ABC", bg=CARD, fg=NAVY, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(
            card,
            text=f"Správně: {self.abc_correct}/{len(self.abc_questions)} | {format_num(percent,1)} %",
            bg=CARD,
            fg=INK,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", pady=(12, 4))
        tk.Label(
            card,
            text=f"Špatně: {len(self.abc_questions) - self.abc_correct}",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 12),
        ).pack(anchor="w", pady=(0, 18))

        buttons = tk.Frame(card, bg=CARD)
        buttons.pack(fill="x", pady=(16, 0))
        tk.Button(buttons, text="Jet znovu ABC", command=self.start_abc, bg=BLUE, fg="white", relief="flat", padx=18, pady=12, cursor="hand2", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 8))
        tk.Button(buttons, text="Jít na testy", command=self.show_test_list, bg=TEAL, fg="white", relief="flat", padx=18, pady=12, cursor="hand2", font=("Segoe UI", 11, "bold")).pack(side="left", padx=8)
        tk.Button(buttons, text="Domů", command=self.show_home, bg=GREEN, fg="white", relief="flat", padx=18, pady=12, cursor="hand2", font=("Segoe UI", 11, "bold")).pack(side="left", padx=8)

    def show_test_list(self) -> None:
        self._clear_center()
        scroll = ScrollableFrame(self.center, bg=BG)
        scroll.pack(fill="both", expand=True, padx=24, pady=24)

        header = tk.Frame(scroll.inner, bg=BG)
        header.pack(fill="x", pady=(0, 18))
        completed = sum(1 for value in self.progress_state.get("tests", {}).values() if value.get("completed"))
        tk.Label(header, text="Maturitní testy", bg=BG, fg=NAVY, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(
            header,
            text=f"Vyber jeden z 20 testů. Hotové testy zůstávají zelené. Aktuálně hotovo {completed}/20.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(6, 0))

        grid = tk.Frame(scroll.inner, bg=BG)
        grid.pack(fill="both", expand=True)
        for col in range(2):
            grid.grid_columnconfigure(col, weight=1)

        for index, test in enumerate(ALL_TESTS):
            bucket = ensure_test_bucket(self.progress_state, test.test_id)
            score = f"{bucket.get('best_score', 0)}/{bucket.get('total', 0)}"
            if bucket.get("completed"):
                bg_color = GREEN
                fg_color = "white"
                status = f"Hotovo | {score}"
            elif bucket.get("best_score", 0) > 0:
                bg_color = "#FFF3CD"
                fg_color = INK
                status = f"Rozdělané | {score}"
            else:
                bg_color = CARD
                fg_color = INK
                status = "Ještě nezkoušeno"
            button = tk.Button(
                grid,
                text=f"{test.title} | β = {format_num(test.beta,2)}\n{status}",
                command=lambda tid=test.test_id: self.open_test(tid),
                bg=bg_color,
                fg=fg_color,
                relief="flat",
                justify="left",
                anchor="w",
                wraplength=430,
                padx=18,
                pady=18,
                cursor="hand2",
                font=("Segoe UI", 14, "bold"),
                highlightbackground=LINE,
                highlightthickness=1,
            )
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=8, pady=8)

    def open_test(self, test_id: int) -> None:
        self.current_test_id = test_id
        self.current_test_entries = {}
        self.current_test_results = []
        self.current_test_explanation_shown = False

        test = ALL_TESTS[test_id - 1]
        solved = ALL_SOLUTIONS[test_id]
        bucket = ensure_test_bucket(self.progress_state, test_id)
        saved_answers = bucket.get("answers", {})

        self._clear_center()
        scroll = ScrollableFrame(self.center, bg=BG)
        scroll.pack(fill="both", expand=True, padx=24, pady=24)

        header_card = tk.Frame(scroll.inner, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=24, pady=24)
        header_card.pack(fill="x", pady=(0, 16))
        tk.Label(header_card, text=test.title, bg=CARD, fg=NAVY, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(
            header_card,
            text="Vyplň závěrečné odpovědi ke každému stroji. Po kliknutí na Vyhodnotit dostaneš správně/špatně a celé řešení krok po kroku.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 11),
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(6, 12))
        tk.Label(
            header_card,
            text=f"Součinitel současnosti pro tento test: β = {format_num(test.beta,2)}",
            bg=CARD,
            fg=INK,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        controls = tk.Frame(header_card, bg=CARD)
        controls.pack(fill="x")
        status_text = "Hotový test" if bucket.get("completed") else f"Nejlepší pokus: {bucket.get('best_score', 0)}/{bucket.get('total', 0)}"
        self.test_score_var = tk.StringVar(value=status_text)
        tk.Label(controls, textvariable=self.test_score_var, bg=BG, fg=INK, font=("Segoe UI", 11, "bold"), padx=14, pady=10).pack(side="left")
        tk.Button(controls, text="Zpět na testy", command=self.show_test_list, bg=BLUE, fg="white", relief="flat", padx=16, pady=10, cursor="hand2", font=("Segoe UI", 10, "bold")).pack(side="right", padx=(8, 0))
        tk.Button(controls, text="Vyhodnotit", command=self.evaluate_current_test, bg=GREEN, fg="white", relief="flat", padx=16, pady=10, cursor="hand2", font=("Segoe UI", 10, "bold")).pack(side="right", padx=(8, 0))
        self.test_reason_button = tk.Button(controls, text="Odůvodnění", command=self.toggle_test_explanation, state="disabled", bg=AMBER, fg="white", relief="flat", padx=16, pady=10, cursor="hand2", font=("Segoe UI", 10, "bold"))
        self.test_reason_button.pack(side="right", padx=(8, 0))
        tk.Button(controls, text="Vyčistit", command=self.clear_test_entries, bg=RED, fg="white", relief="flat", padx=16, pady=10, cursor="hand2", font=("Segoe UI", 10, "bold")).pack(side="right", padx=(8, 0))

        if test_id == 1:
            images_card = tk.Frame(scroll.inner, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=24, pady=20)
            images_card.pack(fill="x", pady=(0, 16))
            tk.Label(images_card, text="Originální obrázky zadání", bg=CARD, fg=INK, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 10))
            row = tk.Frame(images_card, bg=CARD)
            row.pack(fill="x")
            for filename in TEST_IMAGE_FILES:
                photo = load_photo(bundle_dir() / filename, (420, 240))
                if photo is None:
                    continue
                self.photo_refs.append(photo)
                box = tk.Label(row, image=photo, bg=CARD)
                box.pack(side="left", padx=(0, 12))

        for device_key, label in DEVICE_ORDER:
            card = tk.Frame(scroll.inner, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=24, pady=20)
            card.pack(fill="x", pady=(0, 16))
            tk.Label(card, text=label, bg=CARD, fg=INK, font=("Segoe UI", 17, "bold")).pack(anchor="w")
            tk.Label(
                card,
                text=solved[device_key]["task_text"],
                bg=CARD,
                fg=MUTED,
                font=("Segoe UI", 10),
                wraplength=920,
                justify="left",
            ).pack(anchor="w", pady=(4, 14))

            fields = tk.Frame(card, bg=CARD)
            fields.pack(fill="x")
            for col in range(4):
                fields.grid_columnconfigure(col, weight=1)

            for index, field in enumerate(TEST_FIELD_DEFS):
                row = (index // 2) * 2
                column = (index % 2) * 2
                tk.Label(fields, text=field["label"], bg=CARD, fg=INK, font=("Segoe UI", 10, "bold")).grid(row=row, column=column, sticky="w", padx=(0, 10), pady=(0, 4))
                entry = tk.Entry(fields, font=("Consolas", 11), relief="solid", bd=1)
                entry.grid(row=row + 1, column=column, sticky="ew", padx=(0, 20), pady=(0, 14), ipadx=4, ipady=5)
                saved = saved_answers.get(f"{device_key}.{field['key']}", "")
                if saved:
                    entry.insert(0, saved)
                self.current_test_entries[(device_key, field["key"])] = entry

        final_card = tk.Frame(scroll.inner, bg=CARD, highlightbackground=LINE, highlightthickness=1, padx=24, pady=20)
        final_card.pack(fill="x", pady=(0, 16))
        tk.Label(final_card, text="Závěr celého testu", bg=CARD, fg=INK, font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(
            final_card,
            text=f"Nakonec napiš výsledný současný příkon celé soustavy pro β = {format_num(test.beta,2)}.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 12))
        tk.Label(final_card, text=FINAL_FIELD_DEF["label"], bg=CARD, fg=INK, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        final_entry = tk.Entry(final_card, font=("Consolas", 12), relief="solid", bd=1)
        final_entry.pack(fill="x", pady=(4, 8), ipady=5)
        final_saved = saved_answers.get("final.simultaneous_kw", "")
        if final_saved:
            final_entry.insert(0, final_saved)
        self.current_test_entries[("final", "simultaneous_kw")] = final_entry

        self.test_explanation_frame = tk.Frame(scroll.inner, bg="#FFF8E1", highlightbackground=LINE, highlightthickness=1, padx=18, pady=18)
        self.test_explanation_text = tk.Text(
            self.test_explanation_frame,
            height=24,
            wrap="word",
            bg="#FFF8E1",
            fg=INK,
            font=("Consolas", 10),
            relief="flat",
        )
        explanation_scroll = tk.Scrollbar(self.test_explanation_frame, orient="vertical", command=self.test_explanation_text.yview)
        self.test_explanation_text.configure(yscrollcommand=explanation_scroll.set)
        self.test_explanation_text.pack(side="left", fill="both", expand=True)
        explanation_scroll.pack(side="right", fill="y")

    def clear_test_entries(self) -> None:
        for entry in self.current_test_entries.values():
            entry.delete(0, "end")
            entry.configure(bg="white")
        if hasattr(self, "test_score_var"):
            self.test_score_var.set("Pole vyčištěná.")

    def evaluate_current_test(self) -> None:
        if self.current_test_id is None:
            return

        test = ALL_TESTS[self.current_test_id - 1]
        solved = ALL_SOLUTIONS[self.current_test_id]
        results = []
        answers = {}
        correct = 0

        for device_key, device_label in DEVICE_ORDER:
            solved_device = solved[device_key]
            for field in TEST_FIELD_DEFS:
                entry = self.current_test_entries[(device_key, field["key"])]
                raw_value = entry.get().strip()
                answers[f"{device_key}.{field['key']}"] = raw_value
                expected = field["getter"](solved_device)
                ok, expected_text = check_field_answer(field, raw_value, expected)
                entry.configure(bg="#E7F8EA" if ok else "#FBE5E5")
                if ok:
                    correct += 1
                results.append(
                    {
                        "device": device_key,
                        "device_label": device_label,
                        "field_key": field["key"],
                        "field_label": field["label"],
                        "user": raw_value,
                        "expected": expected_text,
                        "ok": ok,
                    }
                )

        final_entry = self.current_test_entries[("final", "simultaneous_kw")]
        final_raw = final_entry.get().strip()
        answers["final.simultaneous_kw"] = final_raw
        final_ok, final_expected = check_field_answer(FINAL_FIELD_DEF, final_raw, solved["simultaneous_kw"])
        final_entry.configure(bg="#E7F8EA" if final_ok else "#FBE5E5")
        if final_ok:
            correct += 1
        results.append(
            {
                "device": "final",
                "device_label": "Závěr",
                "field_key": "simultaneous_kw",
                "field_label": FINAL_FIELD_DEF["label"],
                "user": final_raw,
                "expected": final_expected,
                "ok": final_ok,
            }
        )

        total = len(results)
        percent = 100 * correct / max(1, total)
        bucket = ensure_test_bucket(self.progress_state, self.current_test_id)
        bucket["answers"] = answers
        bucket["best_score"] = max(bucket.get("best_score", 0), correct)
        bucket["total"] = total
        if correct == total:
            bucket["completed"] = True
        save_state(self.progress_state)

        self.current_test_results = results
        self.test_reason_button.configure(state="normal")
        self.test_score_var.set(f"Výsledek: {correct}/{total} | {format_num(percent,1)} %")

        explanation = build_test_solution_text(test, solved, results)
        self.test_explanation_text.configure(state="normal")
        self.test_explanation_text.delete("1.0", "end")
        self.test_explanation_text.insert("1.0", explanation)
        self.test_explanation_text.configure(state="disabled")

        if self.current_test_explanation_shown:
            self.test_explanation_frame.pack_forget()
            self.test_explanation_frame.pack(fill="both", expand=True, pady=(0, 16))

    def toggle_test_explanation(self) -> None:
        if self.test_reason_button.cget("state") == "disabled":
            return
        if self.current_test_explanation_shown:
            self.test_explanation_frame.pack_forget()
            self.current_test_explanation_shown = False
        else:
            self.test_explanation_frame.pack(fill="both", expand=True, pady=(0, 16))
            self.current_test_explanation_shown = True

    def on_close(self) -> None:
        save_state(self.progress_state)
        self.destroy()


def main() -> None:
    app = MotorQuizApp()
    app.mainloop()


if __name__ == "__main__":
    main()
