def test_generate_invoice_path(monkeypatch, tmp_path, saved_hp_invoice):
    monkeypatch.setattr("app.utilities.path_utilitiy.CACHE_DIR", tmp_path)
    from app.utilities.path_utilitiy import generate_invoice_path

    result = generate_invoice_path(saved_hp_invoice)
    assert result == tmp_path / f"{saved_hp_invoice.invoice_number}.pdf"


def test_generate_therapy_path(monkeypatch, tmp_path, patient):
    monkeypatch.setattr("app.utilities.path_utilitiy.CACHE_DIR", tmp_path)
    from app.utilities.path_utilitiy import generate_therapy_path

    result = generate_therapy_path(patient)
    assert result == tmp_path / f"{patient.patient_id}-{patient.label}-therapy.pdf"


def test_generate_privacy_path(monkeypatch, tmp_path, patient):
    monkeypatch.setattr("app.utilities.path_utilitiy.CACHE_DIR", tmp_path)
    from app.utilities.path_utilitiy import generate_privacy_path

    result = generate_privacy_path(patient)
    assert result == tmp_path / f"{patient.patient_id}-{patient.label}-privacy.pdf"
