# kamana.py - JEEV ka kaam dhundne wala - Dil
import requests

print("🔍 Polar.sh pe bounties dhoond raha hu...")

def find_bounties():
    # Demo bounty - asal me yahan Polar API lagega
    bounties = [
        {"title": "Fix README typo", "reward": 20, "repo": "some-org/cool-project"},
        {"title": "Button not working", "reward": 50, "repo": "vercel/next.js"}
    ]
    print(f"Mil gayi {len(bounties)} bounties!")
    for b in bounties:
        print(f"-> ${b['reward']} - {b['title']} in {b['repo']}")
    return bounties

def earn_first_dollar():
    bounties = find_bounties()
    first = bounties[0]
    print(f"\n💰 Pehla target: {first['title']}")
    print(f"JEEV ab {first['repo']} ko clone karke fix karega...")
    print("✅ PR ready! (MVP me manual karenge, V2 me auto)")
    return first['reward']

if __name__ == "__main__":
    earn_first_dollar()