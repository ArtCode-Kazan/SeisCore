import struct


path = '/media/michael/SADYKOV_128/9192/нет_синхронизации/41_SigmaN0016_2020-12-16_34-74-40.bin'
out_path = '/media/michael/SADYKOV_128/9192/нет_' \
           'синхронизации/41_SigmaN0016_2020-12-16_34-74-40_modified.bin'

chunk_size = 1024
with open(path, 'rb') as input_file:
    with open(out_path, 'wb') as out_file:
        record = input_file.read(60)
        out_file.write(record)
        input_file.read(8)
        record = struct.pack('I', 201216)
        out_file.write(record)
        record = struct.pack('I', 74440)
        out_file.write(record)

        while True:
            record = input_file.read(chunk_size)
            if not record:
                break
            out_file.write(record)
