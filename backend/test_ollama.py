from app.services.ai_agent.ai_service import run_ai

result = run_ai("D:/Laptop_backup/D/Alaa_All_D/college/Grad/GitHub/gene-graph-cure/backend/app/data/output")

print("\n=== EXPLANATION ===\n")
print(result["explanation"])

print("\n=== EVIDENCE ===\n")
print(result["evidence"])