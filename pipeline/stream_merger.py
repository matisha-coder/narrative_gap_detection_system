#This is a merger that merges both the website and linkedin data into a single json file. 
#The objective of this code is to merge the data from the website and linkedin and store it in a structured format.

import json
import os

def finalize_module_1_pipeline(
    web_path="add your website data json path here",
    linkedin_path="Add your linkedin data json path here",
    final_out="UPDATTE_YOUR_STORAGE_PATH/"
):
    print("====================================================")
    print("         MODULE 1: MULTI-STREAM PIPELINE MERGER     ")
    print("====================================================\n")

    try:
        # 1. Read Internal Reality data from My Drive
        if not os.path.exists(web_path):
            print(f"[!] Error: Could not find website cache at cloud path:\n    '{web_path}'")
            print("    Please ensure 'website_data.json' is inside your Kleosly_projects folder.")
            return

        with open(web_path, "r", encoding="utf-8") as f:
            web_payload = json.load(f)
        print(f"[+] Successfully loaded Internal Reality data from My Drive.")

        # 2. Read External Perception data from My Drive
        if not os.path.exists(linkedin_path):
            print(f"[!] Error: Synced LinkedIn file missing at cloud path:\n    '{linkedin_path}'")
            print("    Please ensure 'linkedin_data_hand_off.json' is uploaded to the same folder.")
            return

        with open(linkedin_path, "r", encoding="utf-8") as f:
            li_payload = json.load(f)
        print(f"[+] Successfully loaded External Perception data from My Drive.")

        # 3. Unify both dynamic streams into the core data contract
        master_payload = {
            "company_name": web_payload.get("company", "Unknown Organization"),
            "website_url": web_payload.get("website_url", ""),
            "INTERNAL_REALITY": {
                "total_pages_scraped": web_payload.get("total_pages", 0),
                "pages": web_payload.get("pages", [])
            },
            "EXTERNAL_PERCEPTION": {
                "founder_metadata": li_payload.get("founder_metadata", {}),
                "founder_posts": li_payload.get("founder_posts", []),
                "company_posts": li_payload.get("company_posts", [])
            }
        }

        # 4. Export production payload directly back to My Drive
        with open(final_out, "w", encoding="utf-8") as f:
            json.dump(master_payload, f, indent=2, ensure_ascii=False)

        print("\n====================================================")
        print(f"🎉 SUCCESS: Unified data contract generated in the cloud!")
        print(f"📁 Master Payload Path: '{final_out}'")
        print(f"🏢 Target Company: {master_payload['company_name']}")
        print(f"👤 Target Founder: {master_payload['EXTERNAL_PERCEPTION']['founder_metadata'].get('name', 'Unknown')}")
        print("====================================================")

    except Exception as e:
        print(f"[!] Unhandled pipeline compilation error: {e}")

# Run the merger pipeline natively on your personal drive layout
finalize_module_1_pipeline()