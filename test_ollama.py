import httpx

def test_ollama():
    # TEST avec 127.0.0.1 au lieu de localhost pour forcer l'IPv4
    url_tags = "http://127.0.0.1:11434/api/tags"

    try:
        print(f"🚀 Vérification des modèles sur {url_tags}...")
        with httpx.Client(timeout=60.0) as client:
            response = client.get(url_tags)
            print(f"Code HTTP: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Modèles vus par le serveur API (127.0.0.1) :")
                for m in result.get("models", []):
                    print(f" - {m.get('name')} (Taille: {m.get('size')} octets)")
            else:
                print(f"❌ Erreur: {response.text}")
                
    except Exception as e:
        print(f"💥 Exception fatale : {e}")

if __name__ == "__main__":
    test_ollama()
