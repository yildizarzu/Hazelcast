def base_exp():
    from hazelcast import HazelcastClient
    from hazelcast.predicate import sql

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

    # Map'e veri ekle
    my_map.put("key10", "value11").result()

    # Map'ten veri oku
    value1 = my_map.get("key1").result()
    print(f"Key1: {value1}")

    # Map'ten veri sil
    my_map.delete("key1").result()

    my_map = client.get_map(map_name).blocking()

    # Haritaya birkaç veri ekleyelim
    for i in range(2,10):
        my_map.put(f"key{i}", f"value{i}")

    # Tüm haritayı yazdırma
    entries = my_map.entry_set()
    for key, value in entries:
        print(f"{key}: {value}")

    # Belirli bir kritere göre veri çekme (örneğin, değeri "value5" olan anahtar)
    keys_with_value5 = [key for key in my_map.key_set() if my_map.get(key) == "value5"]
    print(f"Keys with value 'value5': {keys_with_value5}")

    """ put_if_absent : Bir key belirtilen map'te mevcut değilse, belirtilen değeri (value) o key için ekler. Eğer key zaten ma'te mevcutsa, var olan değer değiştirilmez. 
    eşzamanlı yazma işlemlerini yönetmek ve veri tutarlılığını sağlamak için oldukça yararlıdır. 
    Bu metod sayesinde, bir anahtarın değeri sadece o anahtar haritada mevcut değilse güncellenir, bu da veri yarışmalarını (race conditions) önler."""
    # put_if_absent ile veri ekleme
    initial_value = my_map.put_if_absent("key11", "value11")
    print(f"Initial value for 'key1': {initial_value}")  # None (ilk kez eklendiği için)

    # Aynı anahtar için tekrar put_if_absent çağrıldığında
    subsequent_value = my_map.put_if_absent("key11", "valuenew11")
    print(f"Subsequent value for 'key11': {subsequent_value}")  # 'value1' (mevcut değeri döner)


    # SQL predicate kullanarak değerleri 'value1' olan key'leri sorgulayalım
    predicate = sql("this == 'value11'")
    entries = my_map.entry_set(predicate)

    # Sorgu sonuçlarını yazdıralım
    for key, value in entries:
        print(f"{key}: {value}")

    # Hazelcast client'ını kapat
    client.shutdown()


def multitherading_exp():
    """ Multithreading (Çok İplikli):
    Tanım: Aynı işlem içinde birden fazla iş parçacığı (thread) oluşturur. İş parçacıkları aynı belleği ve kaynakları paylaşır.
    Bellek: Tüm iş parçacıkları aynı belleği paylaşır, bu nedenle verilerin paylaşımı kolaydır, ancak bu aynı zamanda veri yarışmalarına ve senkronizasyon sorunlarına yol açabilir.
    Paralellik: Gerçek paralellik sağlamaz (Python Global Interpreter Lock - GIL nedeniyle), ancak I/O-bound (G/Ç tarafından sınırlı) görevlerde verimli olabilir.
    Kullanım Durumları: I/O-bound görevler için uygundur. Ağ işlemleri, dosya okuma/yazma, kullanıcı arayüzü uygulamaları.
    Örnekler: Web sunucuları, veri tabanı sorguları, ağ istemcileri. """

    import hazelcast
    import threading
    import time

    def create_client():
        return hazelcast.HazelcastClient(cluster_members=["hazelcast:5701"], cluster_name="hello-world")

    def task_with_lock(client, task_id):
        lock = client.cp_subsystem.get_lock("my-distributed-lock").blocking()

        try:
            print(f"Task {task_id}: Kilidi almaya çalışıyor...")
            lock.lock()
            print(f"Task {task_id}: Kilit alındı, görev gerçekleştiriliyor...")
            time.sleep(5)  # Görev simülasyonu
            print(f"Task {task_id}: Görev tamamlandı, kilit serbest bırakılıyor...")
        finally:
            lock.unlock()

    def worker(task_id):
        client = create_client()
        task_with_lock(client, task_id)
        client.shutdown()

    if __name__ == "__main__":
        threads = []
        num_threads = 4

        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

def multiprocessing_exp():
    """Multiprocessing (Çok İşlemli):
    Tanım: Her biri ayrı bir Python işlemi olarak çalışan birden fazla işlem oluşturur. Her işlem kendi belleğini ve kaynaklarını kullanır.
    Bellek: Her işlem ayrı bir bellek alanına sahiptir, bu nedenle paylaşılan veri, işlemler arasında kolayca paylaşılamaz. Bunun yerine, işlem arası iletişim mekanizmaları (IPC) kullanılır.
    Paralellik: Gerçek paralellik sağlar çünkü her işlem ayrı bir CPU çekirdeğinde çalışabilir.
    Kullanım Durumları: CPU-bound (CPU tarafından sınırlı) görevler için uygundur. Ağır hesaplama gerektiren işlemler için idealdir.
    Örnekler: Veri işleme, bilimsel hesaplamalar, büyük veri analitiği."""

    import hazelcast
    import multiprocessing
    import time

    def create_client():
        # Hazelcast istemcisini oluşturma
        return hazelcast.HazelcastClient(cluster_members=["hazelcast:5701"], cluster_name="hello-world")

    def task_with_lock(client, task_id):
        lock = client.cp_subsystem.get_lock("my-distributed-lock").blocking()

        try:
            print(f"Task {task_id}: Kilidi almaya çalışıyor...")
            lock.lock()
            print(f"Task {task_id}: Kilit alındı, görev gerçekleştiriliyor...")
            
            # Görevlerinizi burada gerçekleştirin
            time.sleep(5)  # Görev simülasyonu
            print(f"Task {task_id}: Görev tamamlandı, kilit serbest bırakılıyor...")
        finally:
            lock.unlock()

    def worker(task_id):
        client = create_client()
        task_with_lock(client, task_id)
        client.shutdown()

    if __name__ == "__main__":
        processes = []
        num_processes = 4  # Örnek olarak 4 paralel işlem

        for i in range(num_processes):
            p = multiprocessing.Process(target=worker, args=(i,))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

if __name__ == "__main__":
    base_exp()
    multitherading_exp()
    multiprocessing_exp()
    