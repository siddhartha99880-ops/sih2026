import json
from datetime import datetime, timezone
from app.core.firebase import get_firestore_client

def seed():
    db = get_firestore_client()
    now = datetime.now(timezone.utc).isoformat()

    parcels = [
        {
            'id': 'PARCEL-KA-BLR-101',
            'khasra_number': '104/2A',
            'khata_number': 'KH-8821',
            'state': 'Karnataka',
            'district': 'Bengaluru Urban',
            'tehsil': 'Bengaluru North',
            'village': 'Yelahanka',
            'recorded_area_m2': 4250.5,
            'center': {'lat': 13.0997, 'lng': 77.5960},
            'geometry_geojson': json.dumps({
                'type': 'Polygon',
                'coordinates': [[[77.5945, 13.0982], [77.5975, 13.0982], [77.5975, 13.1012], [77.5945, 13.1012], [77.5945, 13.0982]]]
            }),
            'srid': 4326,
            'status': 'VERIFIED',
            'verification_status': 'VERIFIED',
            'confidence_score': 0.96,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'PARCEL-KA-BLR-102',
            'khasra_number': '104/2B',
            'khata_number': 'KH-8822',
            'state': 'Karnataka',
            'district': 'Bengaluru Urban',
            'tehsil': 'Bengaluru North',
            'village': 'Yelahanka',
            'recorded_area_m2': 3120.0,
            'center': {'lat': 13.0997, 'lng': 77.5990},
            'geometry_geojson': json.dumps({
                'type': 'Polygon',
                'coordinates': [[[77.5975, 13.0982], [77.6005, 13.0982], [77.6005, 13.1012], [77.5975, 13.1012], [77.5975, 13.0982]]]
            }),
            'srid': 4326,
            'status': 'NEEDS_REVIEW',
            'verification_status': 'IN_REVIEW',
            'confidence_score': 0.84,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'PARCEL-MH-PUN-201',
            'khasra_number': '45/1',
            'khata_number': 'KH-3011',
            'state': 'Maharashtra',
            'district': 'Pune',
            'tehsil': 'Mulshi',
            'village': 'Hinjawadi',
            'recorded_area_m2': 5800.2,
            'center': {'lat': 18.5930, 'lng': 73.7300},
            'geometry_geojson': json.dumps({
                'type': 'Polygon',
                'coordinates': [[[73.7280, 18.5910], [73.7320, 18.5910], [73.7320, 18.5950], [73.7280, 18.5950], [73.7280, 18.5910]]]
            }),
            'srid': 4326,
            'status': 'CONFLICT',
            'verification_status': 'CONFLICT',
            'confidence_score': 0.72,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'PARCEL-MH-PUN-202',
            'khasra_number': '45/2',
            'khata_number': 'KH-3012',
            'state': 'Maharashtra',
            'district': 'Pune',
            'tehsil': 'Mulshi',
            'village': 'Hinjawadi',
            'recorded_area_m2': 2940.8,
            'center': {'lat': 18.5928, 'lng': 73.7333},
            'geometry_geojson': json.dumps({
                'type': 'Polygon',
                'coordinates': [[[73.7315, 18.5910], [73.7350, 18.5910], [73.7350, 18.5945], [73.7315, 18.5945], [73.7315, 18.5910]]]
            }),
            'srid': 4326,
            'status': 'NEEDS_REVIEW',
            'verification_status': 'IN_REVIEW',
            'confidence_score': 0.81,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'PARCEL-UP-NOI-301',
            'khasra_number': '218/A',
            'khata_number': 'KH-7104',
            'state': 'Uttar Pradesh',
            'district': 'Gautam Buddha Nagar',
            'tehsil': 'Dadri',
            'village': 'Jewar',
            'recorded_area_m2': 12400.0,
            'center': {'lat': 28.1240, 'lng': 77.5540},
            'geometry_geojson': json.dumps({
                'type': 'Polygon',
                'coordinates': [[[77.5500, 28.1200], [77.5580, 28.1200], [77.5580, 28.1280], [77.5500, 28.1280], [77.5500, 28.1200]]]
            }),
            'srid': 4326,
            'status': 'VERIFIED',
            'verification_status': 'VERIFIED',
            'confidence_score': 0.98,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'PARCEL-HR-GUR-401',
            'khasra_number': '14/3',
            'khata_number': 'KH-1902',
            'state': 'Haryana',
            'district': 'Gurugram',
            'tehsil': 'Manesar',
            'village': 'Badha',
            'recorded_area_m2': 6750.0,
            'center': {'lat': 28.3730, 'lng': 76.9230},
            'geometry_geojson': json.dumps({
                'type': 'Polygon',
                'coordinates': [[[76.9200, 28.3700], [76.9260, 28.3700], [76.9260, 28.3760], [76.9200, 28.3760], [76.9200, 28.3700]]]
            }),
            'srid': 4326,
            'status': 'UPLOADED',
            'verification_status': 'PENDING',
            'confidence_score': 0.89,
            'created_at': now,
            'updated_at': now
        }
    ]

    for p in parcels:
        db.collection('parcels').document(p['id']).set(p)

    documents = [
        {
            'id': 'DOC-2026-001',
            'parcel_id': 'PARCEL-KA-BLR-101',
            'original_filename': 'Sale_Deed_Yelahanka_104_2A.pdf',
            'mime_type': 'application/pdf',
            'file_size_bytes': 2451200,
            'document_type': 'SALE_DEED',
            'status': 'OCR_COMPLETE',
            'checksum_sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'DOC-2026-002',
            'parcel_id': 'PARCEL-KA-BLR-101',
            'original_filename': 'Cadastral_Survey_Map_Sheet12.png',
            'mime_type': 'image/png',
            'file_size_bytes': 3820400,
            'document_type': 'SURVEY_MAP',
            'status': 'VALIDATED',
            'checksum_sha256': 'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'DOC-2026-003',
            'parcel_id': 'PARCEL-MH-PUN-201',
            'original_filename': 'Satbara_7_12_Extract_Hinjawadi.pdf',
            'mime_type': 'application/pdf',
            'file_size_bytes': 1180200,
            'document_type': 'LAND_RECORD',
            'status': 'NEEDS_REVIEW',
            'checksum_sha256': '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'DOC-2026-004',
            'parcel_id': 'PARCEL-UP-NOI-301',
            'original_filename': 'Khasra_Khatauni_Jewar_Airport_Zone.pdf',
            'mime_type': 'application/pdf',
            'file_size_bytes': 4210000,
            'document_type': 'KHASRA',
            'status': 'VALIDATED',
            'checksum_sha256': 'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'DOC-2026-005',
            'parcel_id': 'PARCEL-HR-GUR-401',
            'original_filename': 'Jamabandi_Fard_Manesar_Sector_84.pdf',
            'mime_type': 'application/pdf',
            'file_size_bytes': 1950000,
            'document_type': 'KHATA',
            'status': 'READY_FOR_OCR',
            'checksum_sha256': 'b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b4447d7322',
            'created_at': now,
            'updated_at': now
        }
    ]

    for d in documents:
        db.collection('documents').document(d['id']).set(d)

    infrastructure = [
        {
            'id': 'INFRA-NH-44-EXP',
            'name': 'NH-44 North-South Corridor Highway Widening',
            'project_type': 'HIGHWAY',
            'status': 'SURVEY_IN_PROGRESS',
            'corridor_geojson': json.dumps({
                'type': 'LineString',
                'coordinates': [[77.5900, 13.0900], [77.5960, 13.1000], [77.6020, 13.1100]]
            }),
            'srid': 4326,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'INFRA-PUN-METRO-PH3',
            'name': 'Pune Metro Line 3 Hinjawadi-Shivajinagar Spur',
            'project_type': 'METRO_RAIL',
            'status': 'UNDER_CONSTRUCTION',
            'corridor_geojson': json.dumps({
                'type': 'LineString',
                'coordinates': [[73.7250, 18.5880], [73.7310, 18.5930], [73.7380, 18.5990]]
            }),
            'srid': 4326,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': 'INFRA-NIA-EXPRESSWAY',
            'name': 'Noida International Airport Jewar Link Expressway',
            'project_type': 'EXPRESSWAY',
            'status': 'PLANNED',
            'corridor_geojson': json.dumps({
                'type': 'LineString',
                'coordinates': [[77.5450, 28.1150], [77.5540, 28.1240], [77.5620, 28.1320]]
            }),
            'srid': 4326,
            'created_at': now,
            'updated_at': now
        }
    ]

    for inf in infrastructure:
        db.collection('infrastructure').document(inf['id']).set(inf)

    validations = [
        {
            'id': 'PARCEL-KA-BLR-101',
            'parcel_id': 'PARCEL-KA-BLR-101',
            'geometry_valid': True,
            'calculated_area_m2': 4248.8,
            'recorded_area_m2': 4250.5,
            'area_difference_m2': 1.7,
            'area_difference_percent': 0.04,
            'overlap_detected': False,
            'overlapping_parcel_ids': [],
            'overlap_results': [],
            'result': 'PASS',
            'summary': 'Parcel boundary geometry is topologically valid. Area matches deed record within 0.04% tolerance. No overlaps detected.',
            'findings': [
                {
                    'code': 'GEOMETRY_VALID',
                    'severity': 'PASS',
                    'message': 'Polygon is closed, valid coordinates, no self-intersection.'
                },
                {
                    'code': 'AREA_MATCH',
                    'severity': 'PASS',
                    'message': 'Recorded area 4250.5 m² matches calculated GIS area 4248.8 m².'
                }
            ],
            'overall_severity': 'PASS'
        },
        {
            'id': 'PARCEL-MH-PUN-201',
            'parcel_id': 'PARCEL-MH-PUN-201',
            'geometry_valid': True,
            'calculated_area_m2': 5800.2,
            'recorded_area_m2': 5800.2,
            'area_difference_m2': 0.0,
            'area_difference_percent': 0.0,
            'overlap_detected': True,
            'overlapping_parcel_ids': ['PARCEL-MH-PUN-202'],
            'overlap_results': [
                {
                    'parcel_id': 'PARCEL-MH-PUN-202',
                    'overlap_area_m2': 485.5,
                    'overlap_percentage': 8.37
                }
            ],
            'result': 'CONFLICT',
            'summary': 'Spatial conflict detected: parcel boundary overlaps with adjacent Khasra 45/2 by 485.5 m² (8.37%). Tehsildar survey field inspection required.',
            'findings': [
                {
                    'code': 'BOUNDARY_OVERLAP',
                    'severity': 'CONFLICT',
                    'message': 'Overlap of 485.5 m² with PARCEL-MH-PUN-202 along eastern boundary.',
                    'intersection_area_m2': 485.5,
                    'intersection_percentage': 8.37
                }
            ],
            'overall_severity': 'CONFLICT'
        }
    ]

    for v in validations:
        db.collection('validations').document(v['id']).set(v)

    print("Firestore seeded successfully!")

if __name__ == '__main__':
    seed()
