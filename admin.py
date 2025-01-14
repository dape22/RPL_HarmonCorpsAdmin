import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import pandas as pd

# Inisialisasi Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("rpl-edudoexam-58276d3f3b2b.json")
    firebase_admin.initialize_app(cred)

# Inisialisasi Firestore
db = firestore.client()

# Mengambil daftar pengguna yang belum terverifikasi dari Firestore
def get_unverified_users():
    users_ref = db.collection("Absensi Karyawan")
    # Ambil semua dokumen yang status email_verified-nya belum terverifikasi
    query = users_ref.where("status", "==", "Belum terverifikasi")
    docs = query.stream()
    
    users_list = []
    for doc in docs:
        user_data = doc.to_dict()
        user_data["UID"] = doc.id  # Menambahkan UID pengguna untuk referensi
        users_list.append(user_data)
    
    # Mengonversi daftar pengguna menjadi DataFrame untuk ditampilkan
    return pd.DataFrame(users_list)

# Verifikasi email pengguna dan update status di Firestore
def verify_user(uid):
    user = auth.get_user(uid)
    
    # Update email_verified ke True di Firebase Authentication
    auth.update_user(uid, email_verified=True)
    
    # Update status verifikasi di Firestore untuk koleksi "Absensi Karyawan"
    user_ref = db.collection("Absensi Karyawan").document(uid)
    user_ref.update({
        "status": "Sudah terverifikasi"  # Ubah status di Firestore
    })
    
    st.success(f"User with email {user.email} has been verified and updated in Firestore.")

# Interface Streamlit
def main():
    st.title("Admin User Verification")

    # Menampilkan pengguna yang belum terverifikasi
    st.subheader("Users to be Verified:")

    # Ambil pengguna yang belum terverifikasi
    unverified_users_df = get_unverified_users()

    if not unverified_users_df.empty:
        # Menampilkan DataFrame pengguna yang belum terverifikasi
        st.dataframe(unverified_users_df)

        # Pilih pengguna yang akan diverifikasi
        selected_user_email = st.selectbox("Select a user to verify:", unverified_users_df['alamat_email'])

        if st.button("Verify User"):
            # Mendapatkan UID dari pengguna yang dipilih
            selected_user = unverified_users_df[unverified_users_df['alamat_email'] == selected_user_email]
            verify_user(selected_user['UID'].values[0])
    else:
        st.warning("No users found who need verification.")

if __name__ == "__main__":
    main()
