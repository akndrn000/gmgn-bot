# FIX: PYTHONPATH tidak perlu lagi di sini karena sudah di-set di Dockerfile ENV.
# Procfile ini tetap disimpan sebagai fallback jika Railway memilih Procfile
# (misalnya deploy tanpa Docker), PYTHONPATH tetap di-set secara eksplisit.
worker: PYTHONPATH=/app/src python -m gmgn_bot
