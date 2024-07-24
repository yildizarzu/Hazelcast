from hazelcast import HazelcastClient

# Hazelcast client'ını başlat
client = HazelcastClient(
    cluster_members=["hazelcast:5701"],  # Docker ağındaki Hazelcast container ismi ve portu
    cluster_name="hello-world"
)

# Map nesnesini al
map_name = "my-map"
my_map = client.get_map(map_name)

# Map'e veri ekle
my_map.put("key1", "value1").result()

# Map'ten veri oku
value1 = my_map.get("key1").result()
print(f"Key1: {value1}")

# Map'ten veri sil
my_map.delete("key1").result()

# Hazelcast client'ını kapat
client.shutdown()