export function validate(data) {
    const checks = [];

    if (!(((typeof data) === 'object') && data !== null)) {
        checks.push('Data harus berupa object.');
        return checks
    };

    if (!('payer_name' in data)) checks.push('Nama harus diisi.');
    else if ((typeof data.payer_name) !== 'string') checks.push('Nama harus berupa string.');
    else if (data.payer_name.trim().length < 1) checks.push('Nama tidak boleh kosong.');

    if (!(('payer_number' in data) || ('payer_email' in data))) checks.push('Kontak (nomor/email) harus diisi.');
    if (('payer_number' in data) && ![null, undefined].includes(data.payer_number)) {
        if ((typeof data.payer_number) !== 'string') checks.push('Nomor harus berupa string.');
        else if (data.payer_number.trim().length < 1) checks.push('Nomor tidak boleh kosong.');
    };
    if (('payer_email' in data) && ![null, undefined].includes(data.payer_email)) {
        if ((typeof data.payer_email) !== 'string') checks.push('Email harus berupa string.');
        else if (data.payer_email.trim().length < 1) checks.push('Email tidak boleh kosong.');
    };

    if (!('payer_address' in data)) checks.push('Alamat harus diisi.');
    else if ((typeof data.payer_address) !== 'string') checks.push('Alamat harus berupa string.');
    else if (data.payer_address.trim().length < 1) checks.push('Alamat tidak boleh kosong.');

    if (('note' in data) && ![null, undefined].includes(data.note)) {
        if ((typeof data.note) !== 'string') checks.push('Catatan harus berupa string.');
        else if (data.note.trim().length < 1) checks.push('Catatan tidak boleh kosong.');
    };

    if (!('lines' in data)) checks.push('Harus ada lines.');
    else if (!Array.isArray(data.lines)) checks.push('Lines harus berupa array.');
    else if (data.lines.length < 1) checks.push('Lines tidak boleh kosong');
    else data.lines.forEach((line, index) => validateLine(line).forEach(lineCheck => checks.push(`[Baris ${index + 1}] ` + lineCheck)));

    return checks;
};

export function validateLine(line) {
    const checks = [];

    if (!(((typeof line) === 'object') && line !== null)) {
        checks.push('Line harus berupa object.');
        return checks
    };

    if (!('payer_name' in line)) checks.push('Nama harus diisi.');
    else if ((typeof line.payer_name) !== 'string') checks.push('Nama harus berupa string.');
    else if (line.payer_name.trim().length < 1) checks.push('Nama tidak boleh kosong.');

    if (!('category' in line)) checks.push('Kategori harus diisi.');
    else if ((typeof line.category) !== 'string') checks.push('Kategori harus berupa string.');
    else if (line.category.trim().length < 1) checks.push('Kategori tidak boleh kosong.');

    if (!('amount' in line)) checks.push('Jumlah harus diisi.');
    else if ((typeof line.amount) !== 'number') checks.push('Jumlah harus berupa number.');
    else if (line.amount <= 0) checks.push('Jumlah tidak boleh nol.');

    if (!('unit' in line)) checks.push('Satuan harus diisi.');
    else if ((typeof line.unit) !== 'string') checks.push('Satuan harus berupa string.');
    else if (line.unit.trim().length < 1) checks.push('Satuan tidak boleh kosong.');

    if (('note' in line) && ![null, undefined].includes(line.note)) {
        if ((typeof line.note) !== 'string') checks.push('Catatan harus berupa string.');
        else if (line.note.trim().length < 1) checks.push('Catatan tidak boleh kosong.');
    };

    return checks;
};