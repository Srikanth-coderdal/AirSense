"""
Seed Curated Environmental Compliance Data for AirSense.

Populates the compliance_records table with realistic, historically grounded
regulatory actions across key Indian industrial and urban clusters:
- Delhi-NCR (CAQM, CPCB, DPCC, NGT)
- Mumbai-MMR (MPCB, CPCB, NGT)
- Bengaluru (KSPCB, CPCB, NGT)
- Chennai (TNPCB, CPCB, NGT)
- Kolkata (WBPCB, CPCB, NGT)
"""

import os
import sys
import logging
import hashlib
from datetime import date
from pathlib import Path
from typing import List, Dict, Any

import psycopg2
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("AirSenseComplianceSeeder")

# Resolve environment configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DB_NAME = os.getenv("POSTGRES_DB", "airquality_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres_secure_pass")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


COMPLIANCE_RECORDS: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. Delhi-NCR Cluster
    # =========================================================================
    {
        "title": "Closure Order on Unregistered Rolling Mill for Heavy Fuel Oil Usage",
        "authority": "DPCC",
        "category": "Industrial Emissions",
        "details": "DPCC special inspection task force discovered an illegal metal re-rolling unit operating without valid Consent to Operate (CTO) and burning unapproved furnace oil instead of PNG in Bawana Sector 3.",
        "penalty_inr": 500000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2025-02-14",
        "city": "Delhi",
        "lat": 28.7997,
        "lon": 77.0326,
    },
    {
        "title": "CAQM Flying Squad Penalty for Dust Screen Lapse at Anand Vihar Transit Project",
        "authority": "CAQM",
        "category": "Construction Dust Violation",
        "details": "CAQM statutory inspection observed non-deployment of anti-smog water guns and missing 10-meter wind-breaking tin sheets along transit construction corridor, causing severe localized PM10 spikes.",
        "penalty_inr": 1000000.00,
        "status": "Penalty Imposed",
        "issue_date": "2025-05-18",
        "city": "Delhi",
        "lat": 28.6469,
        "lon": 77.3160,
    },
    {
        "title": "Sealing of Illegal Plastic Pyrolysis Unit in Narela Industrial Zone",
        "authority": "CPCB",
        "category": "Industrial Emissions",
        "details": "CPCB central enforcement wing ordered the immediate sealing and power cut of an unauthorized plastic pyrolysis oil distillation plant venting toxic VOCs and dense particulate smoke.",
        "penalty_inr": 2500000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2025-08-04",
        "city": "Delhi",
        "lat": 28.8525,
        "lon": 77.0931,
    },
    {
        "title": "Environmental Compensation Levy on Okhla Waste-to-Energy Incinerator",
        "authority": "NGT",
        "category": "Industrial Emissions",
        "details": "NGT Principal Bench ordered an interim environmental compensation deposit following stack emission breaches exceeding dioxin, furan, and particulate permissible thresholds.",
        "penalty_inr": 5000000.00,
        "status": "Under Review",
        "issue_date": "2025-11-20",
        "city": "Delhi",
        "lat": 28.5302,
        "lon": 77.2713,
    },
    {
        "title": "Prosecution and Closure of Non-Zig-Zag Brick Kilns along NCR Border",
        "authority": "CAQM",
        "category": "Brick Kiln Non-Compliance",
        "details": "CAQM enforcement directive shutting down non-compliant brick kilns near the Sahibabad border operating during seasonal winter restrictions without induced draft zig-zag technology conversion.",
        "penalty_inr": 800000.00,
        "status": "Closed",
        "issue_date": "2026-01-10",
        "city": "Delhi",
        "lat": 28.6712,
        "lon": 77.3785,
    },
    {
        "title": "Impounding of Overaged Commercial Diesel Freight Carriers at Anand Vihar Border",
        "authority": "DPCC",
        "category": "Vehicular Fleet Violation",
        "details": "Joint enforcement drive by DPCC and Transport Department impounded non-BS-VI and overaged commercial diesel transport carriers entering NCT without valid Pollution Under Control (PUC) certificates.",
        "penalty_inr": 300000.00,
        "status": "Closed",
        "issue_date": "2026-04-02",
        "city": "Delhi",
        "lat": 28.6280,
        "lon": 77.3298,
    },

    # =========================================================================
    # 2. Mumbai-MMR Cluster
    # =========================================================================
    {
        "title": "Show-Cause Notice to Chemical Bulk Storage Facility in Mahul Corridor",
        "authority": "MPCB",
        "category": "Industrial Emissions",
        "details": "MPCB issued directive following high ambient toluene and volatile organic compound (VOC) concentrations detected by continuous air quality monitoring stations near Mahul village refinery fence lines.",
        "penalty_inr": 1500000.00,
        "status": "Under Review",
        "issue_date": "2025-03-12",
        "city": "Mumbai",
        "lat": 19.0144,
        "lon": 72.8932,
    },
    {
        "title": "Stop-Work Order on High-Rise Coastal Site for Dust Mitigation Non-Compliance",
        "authority": "MPCB",
        "category": "Construction Dust Violation",
        "details": "MPCB municipal squad issued stop-work notice to a high-rise redevelopment project in Wadala for failing to deploy sensor-activated misting systems, unwashed truck exits, and missing perimeter geotextile screens.",
        "penalty_inr": 750000.00,
        "status": "Penalty Imposed",
        "issue_date": "2025-06-25",
        "city": "Mumbai",
        "lat": 18.9950,
        "lon": 72.8600,
    },
    {
        "title": "Closure Order for Toxic Gas Release from Chemical Synthesis Unit in Taloja MIDC",
        "authority": "MPCB",
        "category": "Industrial Emissions",
        "details": "MPCB regional officer ordered immediate power and water disconnection for a dye intermediate manufacturer in Taloja MIDC after an unscrubbed sulfur dioxide leakage incident.",
        "penalty_inr": 2000000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2025-09-15",
        "city": "Mumbai",
        "lat": 19.0838,
        "lon": 73.1165,
    },
    {
        "title": "NGT Fine on Deonar Landfill Subsurface Fires and Open Refuse Burning",
        "authority": "NGT",
        "category": "Biomass & Waste Burning",
        "details": "NGT Western Zone Bench directed municipal authorities to remediate chronic subsurface combustible refuse fires generating dense toxic smoke plumes over Chembur and Govandi.",
        "penalty_inr": 4000000.00,
        "status": "Closed",
        "issue_date": "2025-12-05",
        "city": "Mumbai",
        "lat": 19.0622,
        "lon": 72.8974,
    },
    {
        "title": "Penalty on Petrochemical Auxiliary Boilers Exceeding SPM Norms",
        "authority": "CPCB",
        "category": "Industrial Emissions",
        "details": "CPCB surprise audit recorded suspended particulate matter in boiler flue gas at 2.4 times the permissible limit at a secondary petrochemical refining unit in Chembur.",
        "penalty_inr": 1200000.00,
        "status": "Penalty Imposed",
        "issue_date": "2026-02-18",
        "city": "Mumbai",
        "lat": 19.0435,
        "lon": 72.8856,
    },
    {
        "title": "Crackdown on Non-Compliant Heavy Commercial Carriers in Bhiwandi Logistics Hub",
        "authority": "MPCB",
        "category": "Vehicular Fleet Violation",
        "details": "Enforcement drive targeted uncertified interstate freight vehicles and visible exhaust smoke violators idling in logistics parks across the Bhiwandi freight corridor.",
        "penalty_inr": 450000.00,
        "status": "Closed",
        "issue_date": "2026-05-30",
        "city": "Mumbai",
        "lat": 19.2967,
        "lon": 73.0631,
    },

    # =========================================================================
    # 3. Bengaluru Cluster
    # =========================================================================
    {
        "title": "Closure Order for Electroplating Units Operating Without Acid Fume Scrubbers in Peenya",
        "authority": "KSPCB",
        "category": "Industrial Emissions",
        "details": "KSPCB inspection detected metal finishing and electroplating facilities discharging untreated toxic acid vapors directly through unapproved roof exhausts in Peenya Phase II.",
        "penalty_inr": 1000000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2025-01-22",
        "city": "Bengaluru",
        "lat": 13.0329,
        "lon": 77.5274,
    },
    {
        "title": "Environmental Fine on Commercial Tech Park Development for Unregulated Earthwork Dust",
        "authority": "KSPCB",
        "category": "Construction Dust Violation",
        "details": "Failure to implement wheel washing facilities, vehicle tarping, and continuous perimeter sprinklers during large-scale excavation in Whitefield EPIP zone.",
        "penalty_inr": 600000.00,
        "status": "Penalty Imposed",
        "issue_date": "2025-04-11",
        "city": "Bengaluru",
        "lat": 12.9863,
        "lon": 77.7340,
    },
    {
        "title": "NGT Directive on Solid Waste Incineration Near Bellandur Catchment",
        "authority": "NGT",
        "category": "Biomass & Waste Burning",
        "details": "NGT order imposing punitive damages on private landholders and waste contractors for repeated open waste burning and plastic smoldering along vacant plots bordering Bellandur-Sarjapur corridor.",
        "penalty_inr": 2000000.00,
        "status": "Closed",
        "issue_date": "2025-07-19",
        "city": "Bengaluru",
        "lat": 12.9260,
        "lon": 77.6762,
    },
    {
        "title": "Notice to Pharmaceutical Formulation Unit for Boiler Emission Non-Compliance",
        "authority": "KSPCB",
        "category": "Industrial Emissions",
        "details": "Stack monitoring at a formulation plant in Bommasandra revealed PM and SO2 emissions significantly higher than CPCB consent parameters.",
        "penalty_inr": 850000.00,
        "status": "Under Review",
        "issue_date": "2025-10-28",
        "city": "Bengaluru",
        "lat": 12.8164,
        "lon": 77.6835,
    },
    {
        "title": "Sealing of Non-Compliant Traditional Clamp Brick Kilns in Hoskote Taluk",
        "authority": "CPCB",
        "category": "Brick Kiln Non-Compliance",
        "details": "Joint squad of CPCB and district revenue authorities sealed traditional FCBTK kilns operating without induced draft conversion and using high-sulfur pet coke fuel.",
        "penalty_inr": 1200000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2026-03-05",
        "city": "Bengaluru",
        "lat": 13.0722,
        "lon": 77.7981,
    },
    {
        "title": "Joint Enforcement Action on Polluting Logistics Truck Fleets at Yeshwanthpur",
        "authority": "KSPCB",
        "category": "Vehicular Fleet Violation",
        "details": "Targeted enforcement against heavy diesel cargo fleets failing smoke opacity tests and lacking valid green emission certificates near Yeshwanthpur Wholesale Market.",
        "penalty_inr": 350000.00,
        "status": "Closed",
        "issue_date": "2026-06-14",
        "city": "Bengaluru",
        "lat": 13.0238,
        "lon": 77.5503,
    },

    # =========================================================================
    # 4. Chennai Cluster
    # =========================================================================
    {
        "title": "Closure Order on Organic Petrochemical Intermediate Unit in Manali Corridor",
        "authority": "TNPCB",
        "category": "Industrial Emissions",
        "details": "Continuous Ambient Air Quality Monitoring Station (CAAQMS) identified episodic volatile organic compound (VOC) and mercaptan spikes tracing to poorly sealed distillation columns in Manali industrial complex.",
        "penalty_inr": 3000000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2025-02-28",
        "city": "Chennai",
        "lat": 13.1678,
        "lon": 80.2605,
    },
    {
        "title": "NGT Southern Bench Penalty on Coal Ash Dust Fugitive Emissions at Ennore",
        "authority": "NGT",
        "category": "Industrial Emissions",
        "details": "NGT Southern Zone directed thermal power station management to deposit environmental compensation for dry fly ash blown into coastal wetlands and residential hamlets during dry season.",
        "penalty_inr": 4500000.00,
        "status": "Penalty Imposed",
        "issue_date": "2025-05-09",
        "city": "Chennai",
        "lat": 13.2195,
        "lon": 80.3228,
    },
    {
        "title": "Show-Cause Notice on Secondary Aluminum Casting Unit in Ambattur Estate",
        "authority": "TNPCB",
        "category": "Industrial Emissions",
        "details": "TNPCB inspection found non-functional baghouse dust collectors and unauthorized furnace melting operations resulting in heavy black smoke emissions.",
        "penalty_inr": 500000.00,
        "status": "Under Review",
        "issue_date": "2025-08-27",
        "city": "Chennai",
        "lat": 13.1143,
        "lon": 80.1548,
    },
    {
        "title": "Penalty on Highway Flyover Contractor for Inadequate Water Misting on GST Road",
        "authority": "TNPCB",
        "category": "Construction Dust Violation",
        "details": "Contractor penalized for uncontrolled silica and dust dispersal during girder installation and unpaved service lane transit without water sprinklers near Guindy junction.",
        "penalty_inr": 400000.00,
        "status": "Closed",
        "issue_date": "2025-11-14",
        "city": "Chennai",
        "lat": 13.0067,
        "lon": 80.2025,
    },
    {
        "title": "CPCB Statutory Notice on Auto Components Electro-Deposition Plant in Sriperumbudur",
        "authority": "CPCB",
        "category": "Industrial Emissions",
        "details": "Online Continuous Emission Monitoring Systems (OCEMS) tampering detected during CPCB remote audit, masking VOC and particulate releases.",
        "penalty_inr": 1800000.00,
        "status": "Penalty Imposed",
        "issue_date": "2026-01-28",
        "city": "Chennai",
        "lat": 12.9184,
        "lon": 79.9419,
    },
    {
        "title": "Enforcement Drive Against High-Emission Container Haulage Trucks at Madhavaram",
        "authority": "TNPCB",
        "category": "Vehicular Fleet Violation",
        "details": "Joint operation with RTO issuing compounding fines and fitness cancellations for heavily emitting container haulage trucks operating from the Madhavaram freight terminal.",
        "penalty_inr": 300000.00,
        "status": "Closed",
        "issue_date": "2026-04-19",
        "city": "Chennai",
        "lat": 13.1482,
        "lon": 80.2314,
    },

    # =========================================================================
    # 5. Kolkata Cluster
    # =========================================================================
    {
        "title": "Closure Directive for Unabated Chromium and Organic Fume Stacks at Leather Complex",
        "authority": "WBPCB",
        "category": "Industrial Emissions",
        "details": "WBPCB regional vigilance division sealed commercial finishing tanneries at Bantala for operating unscrubbed thermal boilers and releasing noxious hydrogen sulfide fumes.",
        "penalty_inr": 2000000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2025-03-02",
        "city": "Kolkata",
        "lat": 22.5186,
        "lon": 88.4725,
    },
    {
        "title": "NGT East Zone Fine on Howrah Foundries for Coal-Fired Cupola Emissions",
        "authority": "NGT",
        "category": "Industrial Emissions",
        "details": "NGT Eastern Zone Bench imposed environmental compensation on a cluster of cast iron foundries in Liluah and Belur operating obsolete cupola furnaces without wet scrubbers.",
        "penalty_inr": 3500000.00,
        "status": "Penalty Imposed",
        "issue_date": "2025-06-08",
        "city": "Kolkata",
        "lat": 22.6247,
        "lon": 88.3475,
    },
    {
        "title": "Penalty on Municipal Waste Contractor for Open Refuse Smoldering at Dhapa Dumpsite",
        "authority": "WBPCB",
        "category": "Biomass & Waste Burning",
        "details": "Surveillance caught systematic nocturnal waste fires across peripheral sectors of Dhapa landfill, triggering hazardous PM2.5 levels along Eastern Metropolitan Bypass.",
        "penalty_inr": 1000000.00,
        "status": "Closed",
        "issue_date": "2025-09-22",
        "city": "Kolkata",
        "lat": 22.5458,
        "lon": 88.4206,
    },
    {
        "title": "Stop-Work Order on Megaproject Site for Fugitive Dust Non-Compliance in New Town",
        "authority": "WBPCB",
        "category": "Construction Dust Violation",
        "details": "Inspection team issued stop-work notice to commercial development in Rajarhat Action Area II for dry mortar handling and unpaved haul roads without tarpaulin covers or water tankers.",
        "penalty_inr": 500000.00,
        "status": "Penalty Imposed",
        "issue_date": "2025-12-14",
        "city": "Kolkata",
        "lat": 22.5867,
        "lon": 88.4754,
    },
    {
        "title": "Closure Notices on Clustered Fixed Chimney Kilns in Dankuni-Hooghly Belt",
        "authority": "CPCB",
        "category": "Brick Kiln Non-Compliance",
        "details": "CPCB regional directorate mandated power disconnection for brick manufacturers operating during non-permitted months and failing transition to zig-zag draught technology.",
        "penalty_inr": 1500000.00,
        "status": "Closure Notice Issued",
        "issue_date": "2026-02-24",
        "city": "Kolkata",
        "lat": 22.6844,
        "lon": 88.2917,
    },
    {
        "title": "Vigilance Drive on Polluting Interstate Freight Vehicles along Kona Expressway",
        "authority": "WBPCB",
        "category": "Vehicular Fleet Violation",
        "details": "WBPCB environmental mobile testing unit and Howrah traffic police conducted surprise opacity checks, penalizing heavy diesel carriers exceeding 65 HSU smoke density.",
        "penalty_inr": 250000.00,
        "status": "Under Review",
        "issue_date": "2026-05-12",
        "city": "Kolkata",
        "lat": 22.5855,
        "lon": 88.2980,
    },
]


def generate_record_id(title: str, issue_date_str: str) -> str:
    """Generate a deterministic, 24-character hex ID based on title and date."""
    unique_key = f"{title.strip().lower()}_{issue_date_str.strip()}"
    digest = hashlib.sha256(unique_key.encode("utf-8")).hexdigest()[:20]
    return f"cmp_{digest}"


def get_db_connection():
    """Establish and return a connection to PostgreSQL."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
    )


def seed_compliance_records(records: List[Dict[str, Any]] = COMPLIANCE_RECORDS) -> Dict[str, int]:
    """
    Idempotently seed curated environmental compliance records into PostgreSQL.

    Checks existence by (title, issue_date) to ensure idempotency.
    Uses PostGIS ST_SetSRID(ST_MakePoint(lon, lat), 4326) to construct geom.
    """
    conn = get_db_connection()
    inserted_count = 0
    skipped_count = 0
    updated_count = 0

    select_sql = """
        SELECT record_id FROM compliance_records
        WHERE title = %s AND issue_date = %s;
    """

    insert_sql = """
        INSERT INTO compliance_records (
            record_id,
            title,
            authority,
            category,
            details,
            penalty_inr,
            status,
            issue_date,
            city,
            geom
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)
        );
    """

    try:
        with conn.cursor() as cur:
            for rec in records:
                record_id = generate_record_id(rec["title"], rec["issue_date"])
                issue_d = date.fromisoformat(rec["issue_date"])

                cur.execute(select_sql, (rec["title"], issue_d))
                existing = cur.fetchone()

                if existing:
                    logger.debug(
                        "Record '%s' on %s already exists (ID: %s). Skipping.",
                        rec["title"], rec["issue_date"], existing[0]
                    )
                    skipped_count += 1
                else:
                    cur.execute(
                        insert_sql,
                        (
                            record_id,
                            rec["title"],
                            rec["authority"],
                            rec["category"],
                            rec["details"],
                            rec["penalty_inr"],
                            rec["status"],
                            issue_d,
                            rec["city"],
                            rec["lon"],
                            rec["lat"],
                        ),
                    )
                    inserted_count += 1
                    logger.info(
                        "Inserted record [%s] (%s): %s in %s",
                        record_id, rec["authority"], rec["title"], rec["city"]
                    )

            conn.commit()
            logger.info(
                "Seeding completed. Total: %d, Inserted: %d, Skipped (already present): %d",
                len(records), inserted_count, skipped_count
            )
            return {
                "total": len(records),
                "inserted": inserted_count,
                "skipped": skipped_count,
            }
    except Exception as exc:
        conn.rollback()
        logger.error("Failed to seed compliance records: %s", exc)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    logger.info("Connecting to database '%s' at %s:%s...", DB_NAME, DB_HOST, DB_PORT)
    summary = seed_compliance_records()
    print("\n" + "=" * 60)
    print(f"Compliance Seeding Execution Summary:")
    print(f"  Total Processed: {summary['total']}")
    print(f"  Inserted:        {summary['inserted']}")
    print(f"  Skipped:         {summary['skipped']}")
    print("=" * 60)
