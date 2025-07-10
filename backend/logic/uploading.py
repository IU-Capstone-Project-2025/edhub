from fastapi import UploadFile
import edhub_errors

MAX_SIZE = 5 * 1024 * 1024
CHUNK_SIZE = 64 * 1024


async def careful_upload(file: UploadFile):
    total_size = 0
    chunks = []
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break

        total_size += len(chunk)
        if total_size > MAX_SIZE:
            raise edhub_errors.FileTooLargeException(MAX_SIZE)
        chunks.append(chunk)

    file_data = b''.join(chunks)
    return file_data
