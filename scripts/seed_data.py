"""Seed the RDF knowledge graph with Monsters, Inc. instance data.

Intentional SHACL violations (confirmed by make validate):
  1. Randall Boggs (EMP-009) has mi:assignedStation but no valid TrainingRecord
  2. Door NYC-0099 has mi:lastMaintained > 180 days ago
  3. CDA incident (Q4 2025) reported 75 min after detection (>30 min CDA limit)
"""

import json
from datetime import date, timedelta
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from rich.console import Console
from rich.table import Table

console = Console()

BASE = Path(__file__).parent.parent
MI = Namespace("https://vocab.monstersinc.com/ontology#")
PROV = Namespace("http://www.w3.org/ns/prov#")

COMEDIAN_BASE = "https://vocab.monstersinc.com/comedian/"
DOOR_BASE = "https://vocab.monstersinc.com/door/"
RECORD_BASE = "https://vocab.monstersinc.com/record/"
STATION_BASE = "https://vocab.monstersinc.com/station/"
TRAINING_BASE = "https://vocab.monstersinc.com/training/"
PROFILE_BASE = "https://vocab.monstersinc.com/profile/"
INCIDENT_BASE = "https://vocab.monstersinc.com/incident/"

# Doors that share a logical child profile (for Q7 multi-door detection)
SHARED_PROFILE_DOORS = {"NYC-4821", "NYC-4822", "LAX-0091"}
SHARED_PROFILE_URI = URIRef(PROFILE_BASE + "shared-profile-001")


def add_comedian(g: Graph, m: dict) -> URIRef:
    emp_id = m["id"].lower()
    node = URIRef(COMEDIAN_BASE + emp_id)
    g.add((node, RDF.type, MI.Comedian))
    g.add((node, MI.employeeId, Literal(m["id"])))
    g.add((node, MI.name, Literal(m["name"])))
    if m.get("certLevel") is not None:
        g.add((node, MI.certLevel, Literal(m["certLevel"], datatype=XSD.integer)))
    if m.get("laughScore") is not None:
        g.add((node, MI.currentLaughScore, Literal(m["laughScore"], datatype=XSD.decimal)))
    dept = m.get("department", "LaughOperations")
    dept_uri = URIRef(f"https://vocab.monstersinc.com/ontology#{dept}")
    g.add((node, MI.department, dept_uri))
    return node


def add_door_technician(g: Graph, m: dict) -> URIRef:
    emp_id = m["id"].lower()
    node = URIRef(COMEDIAN_BASE + emp_id)
    g.add((node, RDF.type, MI.DoorTechnician))
    g.add((node, MI.employeeId, Literal(m["id"])))
    g.add((node, MI.name, Literal(m["name"])))
    g.add((node, MI.clearanceLevel, Literal(3, datatype=XSD.integer)))
    # Wire the previously-orphan doorsManaged property onto every technician (Q21).
    g.add((node, MI.doorsManaged, Literal(m.get("doorsManaged", 40), datatype=XSD.integer)))
    dept_uri = URIRef("https://vocab.monstersinc.com/ontology#DoorManagement")
    g.add((node, MI.department, dept_uri))
    return node


def add_monster(g: Graph, m: dict) -> URIRef:
    emp_id = m["id"].lower()
    node = URIRef(COMEDIAN_BASE + emp_id)
    g.add((node, RDF.type, MI.Monster))
    g.add((node, MI.employeeId, Literal(m["id"])))
    g.add((node, MI.name, Literal(m["name"])))
    dept = m.get("department", "LaughOperations")
    dept_uri = URIRef(f"https://vocab.monstersinc.com/ontology#{dept}")
    g.add((node, MI.department, dept_uri))
    return node


def add_station(
    g: Graph, station_id: str, comedian_uri: URIRef, door_uri: URIRef | None = None
) -> URIRef:
    node = URIRef(STATION_BASE + station_id.lower().replace("-", ""))
    g.add((node, RDF.type, MI.LaughFloorStation))
    g.add((node, MI.stationId, Literal(station_id)))
    g.add((node, MI.assignedComedian, comedian_uri))
    g.add((node, MI.shift, MI.AMShift))
    if door_uri:
        g.add((node, MI.activeDoor, door_uri))
    return node


def add_door(g: Graph, d: dict) -> URIRef:
    code = d["portalCode"].replace("-", "").lower()
    node = URIRef(DOOR_BASE + code)
    g.add((node, RDF.type, MI.ChildDoor))
    g.add((node, MI.portalCode, Literal(d["portalCode"])))

    status_map = {
        "active": MI.active,
        "quarantined": MI.quarantined,
        "maintenance": MI.maintenance,
        "decommissioned": MI.decommissioned,
    }
    status_uri = status_map.get(d.get("doorStatus", "active"), MI.active)
    g.add((node, MI.doorStatus, status_uri))

    if d.get("lastMaintained"):
        g.add((node, MI.lastMaintained, Literal(d["lastMaintained"], datatype=XSD.date)))

    # Mint a named URI for ChildProfile (fix 1.5 — no blank nodes)
    portal_code = d["portalCode"]
    if portal_code in SHARED_PROFILE_DOORS:
        profile = SHARED_PROFILE_URI
    else:
        safe_code = portal_code.replace("-", "").lower()
        profile = URIRef(PROFILE_BASE + safe_code)

    g.add((node, MI.childProfile, profile))
    g.add((profile, RDF.type, MI.ChildProfile))
    g.add((profile, MI.ageRange, Literal(d.get("ageRange", "5-7"))))
    g.add((profile, MI.bedroomType, Literal(d.get("bedroomType", "single"))))
    g.add((profile, MI.timezone, Literal(d.get("timezone", "UTC"))))
    # Instance-level data classification (B4) — every child profile is sensitive
    # personal data. Makes disclosure guards queryable at the instance level.
    g.add((profile, MI.dataClassification, MI.SensitivePersonalData))

    return node


def add_performance_record(
    g: Graph, r: dict, comedian_uri: URIRef, rec_date: date, station_uri: URIRef
) -> URIRef:
    rec_id = r["recordId"].lower().replace("-", "")
    node = URIRef(RECORD_BASE + rec_id)
    g.add((node, RDF.type, MI.PerformanceRecord))
    g.add((node, MI.comedian, comedian_uri))
    # BR6 — every PerformanceRecord references the station where it was captured (Q19).
    g.add((node, MI.atStation, station_uri))
    g.add((node, MI.date, Literal(rec_date.isoformat(), datatype=XSD.date)))
    g.add((node, MI.laughScore, Literal(r["laughScore"], datatype=XSD.decimal)))
    g.add((node, MI.energyGenerated, Literal(r["energyGeneratedMwh"], datatype=XSD.decimal)))
    return node


def add_training_record(
    g: Graph,
    comedian_uri: URIRef,
    emp_id: str,
    completed: str,
    expires: str,
    suffix: str = "-cert",
    renewal_offered: bool = True,
    program_uri: URIRef | None = None,
) -> URIRef:
    node = URIRef(TRAINING_BASE + emp_id.lower() + suffix)
    g.add((node, RDF.type, MI.TrainingRecord))
    g.add((node, MI.trainee, comedian_uri))
    g.add((node, MI.completedAt, Literal(completed, datatype=XSD.date)))
    g.add((node, MI.expiresAt, Literal(expires, datatype=XSD.date)))
    g.add((node, MI.renewalOffered, Literal(renewal_offered, datatype=XSD.boolean)))
    # Wire the previously-orphan mi:program link to a TrainingProgram individual (Q20).
    if program_uri is not None:
        g.add((node, MI.program, program_uri))
    return node


def add_wellbeing_pulse(
    g: Graph,
    emp_id: str,
    subject_uri: URIRef,
    score: float,
    dimension: str,
    period: str = "2026-Q2",
) -> URIRef:
    node = URIRef("https://vocab.monstersinc.com/pulse/" + emp_id.lower() + "-" + period.lower())
    g.add((node, RDF.type, MI.WellbeingPulse))
    g.add((node, MI.pulseSubject, subject_uri))
    g.add((node, MI.pulseScore, Literal(score, datatype=XSD.decimal)))
    g.add((node, MI.pulsePeriod, Literal(period)))
    g.add((node, MI.wellbeingDimension, Literal(dimension)))
    return node


def add_cda_incident(
    g: Graph,
    uri_str: str,
    code: str,
    severity: int,
    detected: str,
    reported: str,
    door_uri: URIRef | None = None,
    status: URIRef | None = None,
    resolved: str | None = None,
    responder: URIRef | None = None,
    affected: URIRef | None = None,
) -> URIRef:
    node = URIRef(uri_str)
    g.add((node, RDF.type, MI.CDAIncident))
    g.add((node, MI.incidentCode, Literal(code)))
    g.add((node, MI.severity, Literal(severity, datatype=XSD.integer)))
    g.add((node, MI.detectedAt, Literal(detected, datatype=XSD.dateTime)))
    g.add((node, MI.reportedAt, Literal(reported, datatype=XSD.dateTime)))
    if door_uri:
        g.add((node, MI.involvedDoor, door_uri))
    if status is not None:
        g.add((node, MI.incidentStatus, status))
    if resolved is not None:
        g.add((node, MI.resolvedAt, Literal(resolved, datatype=XSD.dateTime)))
    if responder is not None:
        g.add((node, MI.incidentResponder, responder))
    if affected is not None:
        g.add((node, MI.affectedMonster, affected))
    return node


def main():
    console.rule("[bold blue]Monsters, Inc. — Seeding Knowledge Graph")

    g = Graph()
    g.bind("mi", MI)
    g.bind("prov", PROV)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)

    today = date.today()

    # ── Load source data ──────────────────────────────────────────────────
    monsters_data = json.loads((BASE / "data" / "monsters.json").read_text())
    doors_data = json.loads((BASE / "data" / "doors.json").read_text())
    records_data = json.loads((BASE / "data" / "scare_records.json").read_text())

    # ── Monsters ──────────────────────────────────────────────────────────
    comedian_uris: dict[str, URIRef] = {}
    monster_uris: dict[str, URIRef] = {}
    monster_count = comedian_count = tech_count = 0

    for m in monsters_data:
        if m["type"] == "Comedian":
            node = add_comedian(g, m)
            comedian_uris[m["id"]] = node
            monster_uris[m["id"]] = node
            comedian_count += 1
        elif m["type"] == "DoorTechnician":
            node = add_door_technician(g, m)
            monster_uris[m["id"]] = node
            tech_count += 1
        else:
            node = add_monster(g, m)
            monster_uris[m["id"]] = node
            monster_count += 1

    # ── Training records (valid certs for all comedians EXCEPT Randall) ───
    future_expire = (today + timedelta(days=365)).isoformat()
    past_expire = (today - timedelta(days=30)).isoformat()  # expired

    # Two training programmes, so TrainingProgram coverage is queryable (Q20).
    cert_program = URIRef(TRAINING_BASE + "program-comedy-cert")
    g.add((cert_program, RDF.type, MI.TrainingProgram))
    g.add((cert_program, RDFS.label, Literal("Comedy Certification Programme")))
    conversion_program = URIRef(TRAINING_BASE + "program-scare-to-laugh")
    g.add((conversion_program, RDF.type, MI.TrainingProgram))
    g.add((conversion_program, RDFS.label, Literal("Scare-to-Laughter Conversion Programme")))

    def program_for(employee_id: str) -> URIRef:
        try:
            n = int(employee_id.split("-")[1])
        except (IndexError, ValueError):
            n = 0
        return cert_program if n % 2 == 0 else conversion_program

    for m in monsters_data:
        if m["type"] != "Comedian":
            continue
        emp_id = m["id"]
        comedian_uri = comedian_uris[emp_id]
        program_uri = program_for(emp_id)

        if emp_id == "EMP-009":
            # INTENTIONAL VIOLATION 1: Randall has an expired cert only — and no
            # renewal was offered (at-risk worker without support, for HC3).
            add_training_record(
                g,
                comedian_uri,
                emp_id,
                completed="2022-01-01",
                expires=past_expire,
                renewal_offered=False,
                program_uri=program_uri,
            )
        elif emp_id == "EMP-011":
            # Valid cert PLUS a renewal expiring in 14 days (triggers Q5)
            add_training_record(
                g,
                comedian_uri,
                emp_id,
                completed="2023-01-01",
                expires=future_expire,
                program_uri=program_uri,
            )
            expiring_soon = (today + timedelta(days=14)).isoformat()
            add_training_record(
                g,
                comedian_uri,
                emp_id,
                completed=(today - timedelta(days=351)).isoformat(),
                expires=expiring_soon,
                suffix="-renewal",
                program_uri=program_uri,
            )
        else:
            add_training_record(
                g,
                comedian_uri,
                emp_id,
                completed="2023-01-01",
                expires=future_expire,
                program_uri=program_uri,
            )

    # ── Stations (link comedians who have stationId) ──────────────────────
    station_count = 0
    door_node_map: dict[str, URIRef] = {}
    comedian_station_map: dict[str, URIRef] = {}

    # Build door map first
    for d in doors_data:
        node = add_door(g, d)
        door_node_map[d["portalCode"]] = node

    for m in monsters_data:
        if m["type"] != "Comedian" or not m.get("stationId"):
            continue
        comedian_uri = comedian_uris[m["id"]]
        station_id = m["stationId"]

        door_uri = None
        for d in doors_data:
            if d.get("assignedComedianId") == m["id"]:
                door_uri = door_node_map.get(d["portalCode"])
                break

        station_node = add_station(g, station_id, comedian_uri, door_uri)
        g.add((comedian_uri, MI.assignedStation, station_node))
        comedian_station_map[m["id"]] = station_node
        station_count += 1

    # ── Performance records (spread evenly across the last ~12 months) ────
    # Deterministic even spread by index. Avoids the bunching that occurs when
    # many source records share one date (15 records were dated 2024-03-15),
    # which previously dumped ~390 MWh into the current month (Q6 anomaly).
    record_count = 0
    valid_records = [r for r in records_data if comedian_uris.get(r["comedianId"])]
    n_records = len(valid_records)
    default_station = next(iter(comedian_station_map.values()), None)
    for i, r in enumerate(valid_records):
        comedian_uri = comedian_uris[r["comedianId"]]
        days_back = 1 + round(i * 360 / max(1, n_records - 1))  # 1..361 days ago
        rec_date = today - timedelta(days=days_back)
        station_uri = comedian_station_map.get(r["comedianId"], default_station)
        add_performance_record(g, r, comedian_uri, rec_date, station_uri)
        record_count += 1

    # ── CDA Incidents (distributed across last 4 quarters for Q3) ────────
    # Each incident carries lifecycle data (status, involvedDoor, responder, and
    # where applicable resolvedAt + a CDAComplianceReport) so the contamination,
    # lifecycle and escalation shapes evaluate against real data rather than
    # being vacuously satisfied ("false-clean").

    def dt(d: date, hours: int = 14, minutes: int = 0) -> str:
        return f"{d.isoformat()}T{hours:02d}:{minutes:02d}:00Z"

    # Synthetic quarantined door implicated in incidents — correctly quarantined,
    # so DoorContaminationShape passes. Kept separate from LON-0339, which is left
    # incident-free to demonstrate CV4 (quarantined door with no linked incident).
    inc_door = URIRef(DOOR_BASE + "inc0001")
    g.add((inc_door, RDF.type, MI.ChildDoor))
    g.add((inc_door, MI.portalCode, Literal("INC-0001")))
    g.add((inc_door, MI.doorStatus, MI.quarantined))
    g.add(
        (
            inc_door,
            MI.lastMaintained,
            Literal((today - timedelta(days=20)).isoformat(), datatype=XSD.date),
        )
    )
    inc_profile = URIRef(PROFILE_BASE + "inc0001")
    g.add((inc_door, MI.childProfile, inc_profile))
    g.add((inc_profile, RDF.type, MI.ChildProfile))
    g.add((inc_profile, MI.ageRange, Literal("6-8")))
    g.add((inc_profile, MI.bedroomType, Literal("single")))
    g.add((inc_profile, MI.timezone, Literal("America/New_York")))
    g.add((inc_profile, MI.dataClassification, MI.SensitivePersonalData))

    roz = monster_uris.get("EMP-003")  # CDA Liaison Director — responder
    randall = comedian_uris.get("EMP-009")  # affected comedian

    q2_2026 = today - timedelta(days=49)  # ~7 weeks ago
    q1_2026 = today - timedelta(days=87)  # ~3 months ago
    q4_2025 = today - timedelta(days=198)  # ~6.5 months ago
    q3_2025 = today - timedelta(days=285)  # ~9.5 months ago
    open_recent = today - timedelta(days=45)  # overdue OPEN incident (CV7)

    # Incident 1 — Q2 2026, severity 4, reported on time, escalated (sev>=4)
    # and since resolved (so CV7 — overdue OPEN incidents — excludes it; inc5 is
    # the single intentional overdue-open case).
    inc1_uri = INCIDENT_BASE + f"2319-{q2_2026.strftime('%Y%m%d')}-001"
    add_cda_incident(
        g,
        inc1_uri,
        "2319",
        4,
        detected=dt(q2_2026, 14, 0),
        reported=dt(q2_2026, 14, 22),
        door_uri=inc_door,
        status=MI.Escalated,
        resolved=dt(q2_2026, 16, 0),
        responder=roz,
        affected=randall,
    )

    # Incident 2 — Q1 2026, severity 3, reported on time, closed & resolved
    inc2_uri = INCIDENT_BASE + f"2319-{q1_2026.strftime('%Y%m%d')}-001"
    add_cda_incident(
        g,
        inc2_uri,
        "2319",
        3,
        detected=dt(q1_2026, 9, 0),
        reported=dt(q1_2026, 9, 18),
        door_uri=inc_door,
        status=MI.Closed,
        resolved=dt(q1_2026, 9, 55),
        responder=roz,
    )

    # Incident 3 — Q4 2025, severity 5, LATE reporting (75 min) → SHACL VIOLATION.
    # Escalated and eventually resolved; the late-report violation stands
    # regardless of status (CDAReportingShape is time-based, not status-based).
    inc3_uri = INCIDENT_BASE + f"2319-{q4_2025.strftime('%Y%m%d')}-001"
    add_cda_incident(
        g,
        inc3_uri,
        "2319",
        5,
        detected=dt(q4_2025, 10, 0),
        reported=dt(q4_2025, 11, 15),
        door_uri=inc_door,
        status=MI.Escalated,
        resolved=dt(q4_2025, 12, 30),
        responder=roz,
        affected=randall,
    )

    # Incident 4 — Q3 2025, severity 2, submitted to regulator, resolved, in report
    inc4_uri = INCIDENT_BASE + f"2319-{q3_2025.strftime('%Y%m%d')}-001"
    add_cda_incident(
        g,
        inc4_uri,
        "2319",
        2,
        detected=dt(q3_2025, 15, 30),
        reported=dt(q3_2025, 15, 45),
        door_uri=inc_door,
        status=MI.SubmittedToRegulator,
        resolved=dt(q3_2025, 16, 10),
        responder=roz,
    )

    # Incident 5 — overdue OPEN (45 days old, no resolvedAt) — surfaced by CV7
    inc5_uri = INCIDENT_BASE + f"2319-{open_recent.strftime('%Y%m%d')}-001"
    add_cda_incident(
        g,
        inc5_uri,
        "2319",
        3,
        detected=dt(open_recent, 11, 0),
        reported=dt(open_recent, 11, 12),
        door_uri=inc_door,
        status=MI.Open,
        responder=roz,
    )

    # CDA Compliance Report covering the resolved Q3 incident (report chain)
    report_uri = URIRef("https://vocab.monstersinc.com/report/cda-2025-q3-001")
    g.add((report_uri, RDF.type, MI.CDAComplianceReport))
    g.add((report_uri, MI.submittedAt, Literal(dt(q3_2025, 17, 0), datatype=XSD.dateTime)))
    # Wire the previously-orphan cdaAcknowledgedAt (regulator ack a few days later).
    g.add(
        (
            report_uri,
            MI.cdaAcknowledgedAt,
            Literal(dt(q3_2025 + timedelta(days=3), 12, 0), datatype=XSD.dateTime),
        )
    )
    g.add((report_uri, MI.coversIncident, URIRef(inc4_uri)))
    if roz:
        g.add((report_uri, MI.filedBy, roz))
    g.add((URIRef(inc4_uri), MI.reportedIn, report_uri))

    incident_count = 5

    # ── Org Hierarchy (3.2) ───────────────────────────────────────────────
    sulley = monster_uris.get("EMP-001")
    mike = monster_uris.get("EMP-002")
    # roz (EMP-003) already bound above as the incident responder — reused here.
    celia = monster_uris.get("EMP-006")
    fungus = monster_uris.get("EMP-007")
    needleman = monster_uris.get("EMP-004")

    if sulley:
        g.add((sulley, MI.holdsTitleRole, MI.CEO))
        if mike:
            g.add((sulley, MI.manages, mike))
            g.add((mike, MI.reportsTo, sulley))
            g.add((mike, MI.holdsTitleRole, MI.CCO))
            g.add((MI.LaughOperations, MI.domainOwner, mike))
            g.add((MI.RDLaughter, MI.domainOwner, mike))
        if roz:
            g.add((sulley, MI.manages, roz))
            g.add((roz, MI.reportsTo, sulley))
            g.add((roz, MI.holdsTitleRole, MI.CDADirector))
            g.add((MI.CDACompliance, MI.domainOwner, roz))
        if celia:
            g.add((celia, MI.reportsTo, sulley))
            g.add((celia, MI.holdsTitleRole, MI.ChiefPeopleOfficer))
            g.add((MI.HRTraining, MI.domainOwner, celia))
        if needleman:
            g.add((needleman, MI.reportsTo, sulley))
            g.add((needleman, MI.holdsTitleRole, MI.VPLogistics))
            g.add((MI.DoorManagement, MI.domainOwner, needleman))
        if fungus:
            g.add((fungus, MI.reportsTo, mike))
            g.add((fungus, MI.holdsTitleRole, MI.RDDirector))

    # ── Mid-tier hierarchy + fill the previously un-held roles (D5) ──────────
    jerry = monster_uris.get("EMP-008")  # → VP Energy (owns D1)
    phyllis = monster_uris.get("EMP-022")  # → Floor Manager (HITL recipient)

    if jerry and sulley:
        g.add((jerry, MI.reportsTo, sulley))
        g.add((jerry, MI.holdsTitleRole, MI.VPEnergy))
    if phyllis and celia:
        g.add((phyllis, MI.reportsTo, celia))
        g.add((phyllis, MI.holdsTitleRole, MI.FloorManagerRole))

    # Door technicians report to VP Logistics (Needleman)
    if needleman:
        for tech_id in ("EMP-005", "EMP-020", "EMP-021"):
            t = monster_uris.get(tech_id)
            if t:
                g.add((t, MI.reportsTo, needleman))

    # Rank-and-file comedians report to the Floor Manager (mid-tier depth)
    if phyllis:
        for com_id in (
            "EMP-011",
            "EMP-012",
            "EMP-013",
            "EMP-014",
            "EMP-015",
            "EMP-016",
            "EMP-017",
            "EMP-018",
            "EMP-019",
            "EMP-023",
            "EMP-024",
        ):
            c = comedian_uris.get(com_id)
            if c:
                g.add((c, MI.reportsTo, phyllis))

    # D1 Energy domain owner — now a real role holder (Jerry as VP Energy),
    # not the CEO placeholder.
    if jerry:
        g.add((MI.EnergyProduction, MI.domainOwner, jerry))
    elif sulley:
        g.add((MI.EnergyProduction, MI.domainOwner, sulley))

    # ── Wellbeing pulses (Culture pillar; drives the human-centered queries) ──
    # Mix of healthy and at-risk readings. Low scores (<5.0) surface workers who
    # need support — the counter-signal to pure-yield optimisation.
    pulse_data = [
        ("EMP-001", 8.6, "joy-based performance"),  # Sulley — healthy
        ("EMP-002", 8.1, "psychological safety"),  # Mike — healthy
        ("EMP-009", 3.4, "psychological safety"),  # Randall — at risk
        ("EMP-018", 4.2, "workload sustainability"),  # Lenny — at risk
        ("EMP-019", 4.7, "workload sustainability"),  # Bile — at risk
        ("EMP-013", 5.6, "joy-based performance"),  # Ricky — borderline
    ]
    for emp_id, score, dimension in pulse_data:
        subject = monster_uris.get(emp_id)
        if subject:
            add_wellbeing_pulse(g, emp_id, subject, score, dimension)

    # ── R&D prototypes (D6 — laughter-technique pipeline, Q17) ─────────────
    proto_base = "https://vocab.monstersinc.com/prototype/"
    proto_data = [
        (
            "proto-001",
            "Improvisational Callback Routine",
            MI.approved,
            27.0,
            "Field trial across 12 stations lifted mean yield 27% over the slapstick baseline.",
        ),
        (
            "proto-002",
            "Multi-Sensory Surprise Sequence",
            MI.testing,
            21.0,
            "Controlled lab runs promising; awaiting Laugh Floor pilot sign-off.",
        ),
        (
            "proto-003",
            "Call-and-Response Catchphrase Loop",
            MI.pending,
            15.5,
            "Submitted for R&D cycle review; not yet scheduled for testing.",
        ),
    ]
    for pid, technique, status, yield_target, results in proto_data:
        node = URIRef(proto_base + pid)
        g.add((node, RDF.type, MI.RDPrototype))
        g.add((node, MI.technique, Literal(technique)))
        g.add((node, MI.status, status))
        g.add((node, MI.yieldTarget, Literal(yield_target, datatype=XSD.decimal)))
        g.add((node, MI.testResults, Literal(results)))

    # ── Legacy ScreamCanisters (scare→laughter transformation arc) ─────────
    # A couple of decommissioned fear-era canisters, kept so the pivot from
    # scream energy to laugh energy is queryable (Q18). Disjoint from
    # LaughCanister, so the LaughCanister handling shapes do not target them.
    canister_base = "https://vocab.monstersinc.com/canister/"
    for cid, capacity, fill in [("scream-legacy-001", 12.0, 0.0), ("scream-legacy-002", 12.0, 0.0)]:
        node = URIRef(canister_base + cid)
        g.add((node, RDF.type, MI.ScreamCanister))
        g.add((node, MI.capacity, Literal(capacity, datatype=XSD.decimal)))
        g.add((node, MI.fillLevel, Literal(fill, datatype=XSD.decimal)))
        g.add((node, MI.sealStatus, Literal(True)))
        g.add((node, MI.energyType, MI.screamEnergy))
        g.add((node, RDFS.label, Literal(f"Scream Canister {cid} (legacy)")))

    # ── Serialise ─────────────────────────────────────────────────────────
    out_path = BASE / "data" / "seed_graph.ttl"
    g.serialize(destination=str(out_path), format="turtle")

    # ── Summary table ─────────────────────────────────────────────────────
    table = Table(title="Seed Graph Summary", show_header=True, header_style="bold magenta")
    table.add_column("Entity Type", style="cyan", width=25)
    table.add_column("Count", justify="right", width=8)
    table.add_column("Notes", style="dim")

    table.add_row("mi:Comedian", str(comedian_count), "incl. Sulley, Mike, Randall")
    table.add_row("mi:DoorTechnician", str(tech_count), "incl. Needleman, Smitty")
    table.add_row("mi:Monster", str(monster_count), "incl. Roz, Mike, Celia, Fungus")
    table.add_row("mi:LaughFloorStation", str(station_count), "stations with active comedians")
    table.add_row("mi:ChildDoor", str(len(doors_data)), "50 portals; 3 share a profile (Q7)")
    table.add_row("mi:PerformanceRecord", str(record_count), "dates shifted to last 13 months")
    table.add_row("mi:CDAIncident", str(incident_count), "distributed across 4 quarters (Q3)")
    table.add_row(
        "mi:TrainingRecord",
        str(comedian_count + 1),
        "1 expired (Randall), 1 expiring in 14d (George, Q5)",
    )
    table.add_row("[bold]Total triples[/bold]", f"[bold]{len(g)}[/bold]", "")

    console.print(table)
    console.print(f"\n[green]✓[/green] Written to [bold]{out_path}[/bold]")
    console.print()
    console.print("[bold yellow]Intentional violations (confirmed by make validate):[/bold yellow]")
    console.print(
        "  1. [cyan]Randall Boggs (EMP-009)[/cyan] — assignedStation but TrainingRecord expired → ComedianCertShape"
    )
    console.print(
        "  2. [cyan]Door NYC-0099[/cyan] — lastMaintained 2023-09-01 (>180 days) → DoorDispatchShape"
    )
    console.print(
        "  3. [cyan]CDA incident (Q4 2025)[/cyan] — reported 75 min after detection (>30 min) → CDAReportingShape"
    )
    console.print()


if __name__ == "__main__":
    main()
