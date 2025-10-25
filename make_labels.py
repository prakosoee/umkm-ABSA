import pandas as pd
from transformers import AutoTokenizer
from typing import Dict


class AspectBasedSentimentLabeler:
    """
    Labeling dataset untuk Aspect-Based Sentiment Analysis (ABSA)
    menggunakan pendekatan keyword-based dan optional BERT model.
    """

    def __init__(self, use_bert: bool = False):
        """
        Args:
            use_bert: Jika True, gunakan model BERT untuk labeling otomatis
        """
        self.use_bert = use_bert

        # Definisi aspek untuk review restoran/makanan
        self.aspects = {
            "food_quality": "kualitas_makanan",
            "price": "harga",
            "service": "pelayanan",
            "ambiance": "suasana",
            "portion": "porsi",
        }

        # Keywords untuk setiap aspek dan sentimen
        self.aspect_keywords = {
            "food_quality": {
                    "positive": [
                        "enak",
                        "lezat",
                        "mantap",
                        "nikmat",
                        "segar",
                        "gurih",
                        "empuk",
                        "kres",
                        "juicy",
                        "renyah",
                        "crispy",
                        "sedap",
                        "kompleks",
                        "kaya rasa",
                        "recommended",
                        "rekomen",
                        "wajib coba",
                        "favorit",
                        "juara",
                        "top",
                        "mantul",
                        "enak banget",
                        "nagih",
                        "bikin ketagihan",
                        "super lezat",
                        "mantep pol",
                        "endol",
                        "enak gila",
                        "gokil rasanya",
                        "gaada lawan",
                        "bikin ngiler",
                        "parah enaknya",
                        "maknyus",
                        "nendang",
                        "istimewa",
                        "perfect",
                        "amazing",
                        "super enak",
                        "ok banget",
                        "mantap jiwa",
                        "terbaik",
                        "juara banget",
                        "gila sih ini",
                        "taste-nya dapet",
                        "rasa berasa",
                        "auto repeat order",
                        "rasa mewah",
                        "ga bohong enak",
                        "worth to try",
                        "selalu enak",
                        "ga pernah gagal",
                        "wah parah",
                        "gila enaknya",
                        "tastynya nempel",
                        "meledak di mulut",
                        "full flavor",
                        "rasa kaya",
                        "khas banget",
                        "autobeli lagi",
                        "ga kalah sama resto",
                        "recommended banget",
                        "bumbu nendang",
                        "enak parah",
                        "makin enak",
                        "rasanya pas",
                        "ga kemanisan",
                        "balance banget",
                        "creamy",
                        "lembut",
                        "juicy banget",
                        "super crunchy",
                        "crispy abis",
                        "taste solid",
                        "ngangenin",
                        "perfect balance",
                        "rasa otentik",
                        "fresh banget",
                        "auto lapar",
                        "aromanya menggoda",
                        "ga nyesel beli",
                        "worth it banget",
                        "bikin bahagia",
                        "masih keinget rasanya",
                        "best in town",
                        "kualitas rasa top",
                        "chef’s kiss",
                        "maknyuss",
                        "legit",
                        "authentic",
                        "berasa effort-nya",
                        "rasa nempel di lidah",
                        "autopesan lagi",
                        "full bumbu",
                        "taste mantap",
                        "flavor bomb",
                        "ga bisa berhenti makan",
                        "rasa khas banget",
                        "premium taste",
                        "rasa rich",
                        "wangi menggoda",
                        "juara rasa",
                        "rasa kuat",
                    ],
                    "negative": [
                        "hambar",
                        "tawar",
                        "tidak enak",
                        "ga enak",
                        "kurang enak",
                        "lembek",
                        "alot",
                        "keras",
                        "basi",
                        "amis",
                        "anyir",
                        "pahit",
                        "kurang cocok",
                        "biasa aja",
                        "mengecewakan",
                        "aneh rasanya",
                        "ga jelas",
                        "ga sesuai ekspektasi",
                        "ga worth it",
                        "rasanya aneh",
                        "ga fresh",
                        "kayak basi",
                        "ga matang",
                        "mentah",
                        "kegosongan",
                        "keasinan",
                        "kematangan",
                        "terlalu manis",
                        "ga nyatu rasanya",
                        "aneh banget",
                        "ga berasa",
                        "plain",
                        "kurang gurih",
                        "porsinya aneh",
                        "rasanya hilang",
                        "nggak banget",
                        "bumbunya ga nyatu",
                        "rasa gagal",
                        "ga sesuai harga",
                        "ga nikmat",
                        "asin banget",
                        "manis banget",
                        "ga niat masak",
                        "rasa ancur",
                        "tekstur aneh",
                        "ga karuan",
                        "menjijikkan",
                        "bau amis",
                        "bau tengik",
                        "bau basi",
                        "rasa aneh banget",
                        "ga bisa dimakan",
                        "mual",
                        "bikin eneg",
                        "ga fresh sama sekali",
                        "ga layak makan",
                        "ga rekomen",
                        "mengecewakan banget",
                        "gagal total",
                        "aneh di lidah",
                        "teksturnya salah",
                        "keras banget",
                        "nggak renyah",
                        "ga garing",
                        "kaya plastik",
                        "rasa buatan",
                        "kayak instan",
                        "kurang seasoning",
                        "ga berbumbu",
                        "bumbunya hambar",
                        "aneh banget rasanya",
                        "ga enak parah",
                        "bikin kecewa",
                        "ga bakal beli lagi",
                        "bad taste",
                        "tidak sesuai harapan",
                        "kecewa berat",
                        "overcooked",
                        "undercooked",
                        "ga seimbang",
                        "bumbunya berlebihan",
                        "ga nyatu",
                        "ga banget sih",
                        "ga masuk lidah",
                        "rasa kacau",
                        "flop",
                        "zonk",
                        "menyesal beli",
                        "taste-nya off",
                        "aneh parah",
                        "ga layak jual",
                        "bau aneh",
                        "rasa busuk",
                        "pahit banget",
                        "bau tengik banget",
                        "rasa basi",
                        "ga nyatu banget",
                        "ga sesuai review",
                        "bumbunya aneh",
                    ],
                },
                "price": {
                    "positive": [
                        "murah",
                        "terjangkau",
                        "worth it",
                        "sesuai",
                        "pas",
                        "oke",
                        "affordable",
                        "masuk kantong",
                        "ga mahal",
                        "tidak mahal",
                        "harga bersahabat",
                        "hemat",
                        "ramah kantong",
                        "harga oke",
                        "murah banget",
                        "super worth",
                        "murah meriah",
                        "harga cucok",
                        "value for money",
                        "ekonomis",
                        "harga aman",
                        "ga bikin kantong jebol",
                        "ga overprice",
                        "harga masuk akal",
                        "reasonable",
                        "sepadan",
                        "harga pantas",
                        "good deal",
                        "diskonnya lumayan",
                        "murah tapi enak",
                        "terjangkau banget",
                        "budget friendly",
                        "harga bersahabat banget",
                        "murah pol",
                        "murah tapi mantap",
                        "best deal",
                        "nggak rugi",
                        "bener-bener worth",
                        "murah tapi puas",
                        "mantap harganya",
                        "harga kompetitif",
                        "harga bagus",
                        "deal banget",
                        "ga nyesel beli",
                        "hemat banget",
                        "murah tapi kualitas top",
                        "super value",
                        "harga pas banget",
                        "ngirit tapi nikmat",
                        "murah tapi mewah",
                        "value tinggi",
                        "promo oke",
                        "paket hemat",
                        "harga terbaik",
                        "budget aman",
                        "harga damai",
                        "murah tapi kece",
                        "affordable banget",
                        "hemat parah",
                        "harga cakep",
                        "murah tapi berkelas",
                        "hemat dompet",
                        "value maksimal",
                        "murah tapi worth it",
                        "harga mantap",
                        "murah tapi berkualitas",
                        "super affordable",
                        "ga kemahalan",
                        "murah meriah banget",
                        "super hemat",
                        "hemat cuy",
                        "harga aman banget",
                        "murah cuy",
                        "harga low banget",
                        "murah tapi bagus",
                        "best price",
                        "murah tapi ga murahan",
                        "value-nya dapet",
                        "harga masuk akal banget",
                        "murah bener",
                        "harga manusiawi",
                        "murah tapi puas banget",
                        "murah tapi ga abal-abal",
                        "harga normal",
                        "harga jujur",
                        "harga wajar",
                        "harga sesuai",
                        "murah tapi solid",
                        "murah tapi nikmat",
                        "murah tapi worth every bite",
                        "ngirit tapi puas",
                        "harga masuk di dompet",
                        "murah parah",
                    ],
                    "negative": [
                        "mahal",
                        "kemahalan",
                        "overprice",
                        "tidak sesuai",
                        "ga sesuai",
                        "terlalu mahal",
                        "ga worth",
                        "tidak worth",
                        "harga ga masuk akal",
                        "harga tinggi",
                        "nggak sepadan",
                        "ga sesuai kualitas",
                        "mahal banget",
                        "nggak worth it",
                        "overpriced",
                        "ga sebanding",
                        "kemahalan parah",
                        "nggak pantas",
                        "harga ga logis",
                        "ga sesuai isi",
                        "bikin nyesek",
                        "mahal tapi biasa aja",
                        "nggak sebanding sama rasa",
                        "mahal tapi zonk",
                        "harga nyiksa",
                        "harga bikin mikir",
                        "harga sadis",
                        "mahalnya ga wajar",
                        "ga sesuai ekspektasi",
                        "harga gila",
                        "harga aneh",
                        "harga ngaco",
                        "mahal banget sih",
                        "bikin nyesel",
                        "mahal tapi ga sebanding",
                        "harga ga worth",
                        "nggak layak",
                        "mahal tapi ga enak",
                        "harga kelewatan",
                        "harga parah",
                        "nggak affordable",
                        "nggak ramah kantong",
                        "bikin boncos",
                        "harga ga manusiawi",
                        "harga nggak cocok",
                        "nggak sesuai value",
                        "over banget",
                        "nggak worth sama sekali",
                        "kemahalan sih",
                        "ga sesuai rasa",
                        "harga menipu",
                        "ga pantes segitu",
                        "mahal tapi gagal",
                        "harga ngibul",
                        "ga sepadan banget",
                        "ga make sense",
                        "bikin kantong jebol",
                        "mahal tapi hambar",
                        "ga layak harganya",
                        "ga sebanding sama harga",
                        "harga ajaib",
                        "harga ga fair",
                        "ga cocok kantong",
                        "harga absurd",
                        "ga sesuai dompet",
                        "harga ancur",
                        "ga masuk akal banget",
                        "harga rusak",
                        "harga bikin males",
                        "nggak worth banget",
                        "kemahalan gila",
                        "bikin rugi",
                        "ga sesuai harapan",
                        "mahal padahal biasa aja",
                        "nggak balance",
                        "harga bohong",
                        "harga tipu-tipu",
                        "kemahalan banget",
                        "mahal banget parah",
                        "harga sadis banget",
                        "harga zonk",
                        "harga menyesakkan",
                    ],
                },
                "service": {
                    "positive": [
                        "ramah",
                        "baik",
                        "cepat",
                        "responsif",
                        "sopan",
                        "membantu",
                        "pelayanan baik",
                        "friendly",
                        "helpful",
                        "sigap",
                        "tanggap",
                        "fast response",
                        "cekatan",
                        "niat",
                        "welcome",
                        "ramah banget",
                        "super ramah",
                        "gercep",
                        "nggak nyuekin",
                        "pelayan sopan",
                        "humble",
                        "respons cepat",
                        "niat banget",
                        "mau bantu",
                        "nggak jutek",
                        "sopan banget",
                        "ramah parah",
                        "pelayanan mantap",
                        "respons oke",
                        "melayani dengan baik",
                        "cepat tanggap",
                        "service oke",
                        "service cepat",
                        "customer service mantap",
                        "super helpful",
                        "senyum terus",
                        "positive attitude",
                        "welcome banget",
                        "ramah maksimal",
                        "pelayanannya keren",
                        "cepet banget",
                        "fast banget",
                        "ramah abis",
                        "good attitude",
                        "super niat",
                        "melayani dengan hati",
                        "service bintang lima",
                        "ramah all out",
                        "niat banget pelayanannya",
                        "bikin nyaman",
                        "super fast",
                        "friendly banget",
                        "nggak ribet",
                        "proaktif",
                        "pelayanannya top",
                        "santun",
                        "super baik",
                        "pelayanannya bagus",
                        "ga nunggu lama",
                        "tanggap banget",
                        "ramah gila",
                        "enak komunikasinya",
                        "sigap abis",
                        "pelayanan niat",
                        "ramah total",
                        "ga jutek sama sekali",
                        "super cepat",
                        "melayani maksimal",
                        "helpful banget",
                        "pelayanannya sopan banget",
                        "santai tapi niat",
                        "nggak galak",
                        "sabar banget",
                        "super sabar",
                        "pelayanan tulus",
                        "bener-bener melayani",
                        "care banget",
                        "servicenya the best",
                        "bikin puas",
                        "ramah 10/10",
                        "ramah all staff",
                        "ramah banget pelayannya",
                        "nggak nyolot",
                    ],
                    "negative": [
                        "lambat",
                        "lama",
                        "ketus",
                        "jutek",
                        "tidak ramah",
                        "ga ramah",
                        "pelayanan buruk",
                        "pelayanan kurang",
                        "kurang sopan",
                        "slow",
                        "nyebelin",
                        "galak",
                        "nyolot",
                        "jutek banget",
                        "lama banget",
                        "slow respon",
                        "nggak tanggap",
                        "ga sigap",
                        "pelayanan nyebelin",
                        "ga enak dilayanin",
                        "ga niat",
                        "pelayan jutek",
                        "pelayan ga ramah",
                        "nggak bantu",
                        "service jelek",
                        "ga profesional",
                        "sombong",
                        "pelayanan asal",
                        "pelayanannya buruk",
                        "ga care",
                        "pelayan ngeselin",
                        "nggak sopan banget",
                        "pelayanannya parah",
                        "nggak gercep",
                        "respon lama",
                        "pelayanan lama",
                        "pelayanannya nyebelin",
                        "ga fast response",
                        "ga niat banget",
                        "cuek",
                        "dicuekin",
                        "dibiarkan",
                        "ga tanggap",
                        "ga diperhatiin",
                        "nggak diurus",
                        "pelayan ngelawan",
                        "kasar",
                        "ketus banget",
                        "pelayanan ga sopan",
                        "pelayan songong",
                        "ga ramah banget",
                        "sok sibuk",
                        "ga bantuin",
                        "ga profesional banget",
                        "pelayanannya nyebelin banget",
                        "service parah",
                        "slow banget",
                        "ga sopan",
                        "ga melayani",
                        "pelayanannya ngaco",
                        "nggak niat banget",
                        "pelayan nyolot",
                        "bikin males",
                        "ga diladenin",
                        "nggak responsif",
                        "lama respon banget",
                        "ga peka",
                        "ga gesit",
                        "ga ada inisiatif",
                        "pelayan nyebelin banget",
                        "pelayanannya jelek banget",
                        "ga tanggung jawab",
                        "service gagal",
                        "pelayanannya zonk",
                        "ga mau bantu",
                        "malesin",
                        "ga sopan banget",
                        "pelayanan lambat banget",
                        "bikin kesel",
                        "nggak jelas",
                        "bikin jengkel",
                    ],
                },
                "ambiance": {
                    "positive": [
                        "nyaman",
                        "bersih",
                        "rapi",
                        "cozy",
                        "bagus",
                        "luas",
                        "sejuk",
                        "ber-ac",
                        "tenang",
                        "asri",
                        "aesthetic",
                        "instagramable",
                        "adem",
                        "homey",
                        "keren",
                        "kekinian",
                        "vibes-nya enak",
                        "modern",
                        "suasana santai",
                        "bikin betah",
                        "nyaman banget",
                        "higienis",
                        "rapih",
                        "cakep tempatnya",
                        "dekorasinya bagus",
                        "suasana oke",
                        "vibe positif",
                        "tempat kece",
                        "bersih banget",
                        "wangi",
                        "lighting bagus",
                        "tempat luas",
                        "view bagus",
                        "suasana adem",
                        "ga berisik",
                        "suasana damai",
                        "asik buat nongkrong",
                        "cantik banget",
                        "desainnya oke",
                        "tempatnya nyaman",
                        "vibe-nya dapet",
                        "atmosfer enak",
                        "bagus buat foto",
                        "tempat estetik",
                        "vibe calm",
                        "nyaman parah",
                        "rapi banget",
                        "super cozy",
                        "tempatnya bersih banget",
                        "steril",
                        "nggak pengap",
                        "bikin rileks",
                        "suasana homy",
                        "nyaman buat kerja",
                        "tempatnya santai",
                        "ga bising",
                        "asri banget",
                        "interior keren",
                        "desain interior bagus",
                        "tempat kece banget",
                        "vibe santai",
                        "ga panas",
                        "adem banget",
                        "nyaman paripurna",
                        "tempat hits",
                        "lighting pas",
                        "vibe chill",
                        "suasananya calm",
                        "bersih parah",
                        "tempat modern",
                        "santai banget",
                        "sirkulasi udara bagus",
                        "ruangan wangi",
                        "tempat luas banget",
                        "beneran cozy",
                        "nyaman maksimal",
                        "ruangannya adem",
                        "tempat instagramable banget",
                    ],
                    "negative": [
                        "kotor",
                        "sempit",
                        "panas",
                        "gerah",
                        "berisik",
                        "bising",
                        "tidak nyaman",
                        "ga nyaman",
                        "kumuh",
                        "pengap",
                        "bau",
                        "jorok",
                        "sumpek",
                        "berantakan",
                        "bau asap",
                        "bau rokok",
                        "ga enak dilihat",
                        "kacau",
                        "gelap",
                        "remang",
                        "tempatnya jelek",
                        "suasana ga enak",
                        "ga cozy",
                        "ga aesthetic",
                        "bau amis",
                        "bau got",
                        "bau minyak",
                        "tempat kecil",
                        "rame banget",
                        "bising parah",
                        "ga betah",
                        "bau banget",
                        "jorok parah",
                        "ga bersih",
                        "lantai kotor",
                        "meja kotor",
                        "kursi kotor",
                        "sampah dimana-mana",
                        "ga tertata",
                        "sirkulasi udara jelek",
                        "tempat panas",
                        "ac mati",
                        "ga adem",
                        "ga steril",
                        "ga higienis",
                        "bau apek",
                        "ruangan sumpek",
                        "pengap banget",
                        "ruangannya gelap",
                        "lampu redup",
                        "vibe-nya aneh",
                        "bau aneh",
                        "bikin pusing",
                        "bau parah",
                        "bikin gerah",
                        "ga tenang",
                        "rame parah",
                        "berisik banget",
                        "ga bersih banget",
                        "vibe aneh",
                        "suasana buruk",
                        "vibe jelek",
                        "ga cakep",
                        "ga cocok buat nongkrong",
                        "ga menarik",
                        "tempat ga layak",
                        "jorok banget",
                        "bikin ga betah",
                        "ga nyaman banget",
                        "sumpek banget",
                        "bau nggak enak",
                        "bau pesing",
                        "ruangannya kotor",
                        "tempatnya jelek banget",
                        "ga terawat",
                        "bikin ilfeel",
                        "jorok total",
                        "bau banget sih",
                        "bau parah banget",
                        "ga cozy sama sekali",
                        "ga proper",
                        "bau kenceng",
                        "ruangannya panas",
                    ],
                },
                "portion": {
                    "positive": [
                        "banyak",
                        "pas",
                        "cukup",
                        "mengenyangkan",
                        "sepadan",
                        "berlimpah",
                        "porsinya oke",
                        "ga pelit",
                        "pas banget",
                        "porsinya besar",
                        "porsinya puas",
                        "porsinya mantap",
                        "porsinya banyak",
                        "porsinya seimbang",
                        "ngenyangin",
                        "porsinya lumayan",
                        "porsinya ga nanggung",
                        "beneran kenyang",
                        "value-nya dapet",
                        "porsinya fair",
                        "porsinya worth",
                        "cukup banget",
                        "ga kurang",
                        "porsinya generous",
                        "porsinya top",
                        "porsinya ideal",
                        "nggak dikit",
                        "porsinya berasa",
                        "porsinya mantul",
                        "porsinya lega",
                        "porsinya bikin kenyang",
                        "porsinya ga pelit banget",
                        "porsinya banyak banget",
                        "porsinya ngagetin",
                        "porsinya luar biasa",
                        "porsinya bikin puas",
                        "porsinya sesuai harga",
                        "ga rugi beli",
                        "porsinya gede",
                        "porsinya mantap banget",
                        "nggak nyesel porsi",
                        "porsinya pas di perut",
                        "porsinya ngenyangin banget",
                    ],
                    "negative": [
                        "sedikit",
                        "kecil",
                        "kurang",
                        "ga cukup",
                        "pelit",
                        "porsinya mini",
                        "porsinya dikit",
                        "ga sebanding",
                        "porsinya nyesek",
                        "porsinya kecewa",
                        "porsinya nyeselin",
                        "porsinya ga sesuai harga",
                        "porsinya pelit banget",
                        "ga sepadan",
                        "porsinya ga layak",
                        "ga ngenyangin",
                        "porsinya nanggung",
                        "porsinya parah",
                        "porsinya ngaco",
                        "porsinya kecil banget",
                        "porsinya dikit banget",
                        "porsinya nyesek banget",
                        "porsinya aneh",
                        "ga sesuai harapan",
                        "ga layak",
                        "porsinya bikin kecewa",
                        "ga puas",
                        "porsinya zonk",
                        "ga sebanding harga",
                        "porsinya ga worth",
                        "porsinya ga nyatu",
                        "ga kenyang",
                        "bikin lapar lagi",
                        "ga sesuai review",
                        "porsinya ga wajar",
                        "porsinya sadis",
                        "ga masuk akal",
                        "porsinya ngenes",
                        "porsinya tipis",
                        "porsinya terlalu kecil",
                        "ga puas banget",
                        "porsinya nyedih",
                        "bikin kecewa parah",
                        "porsinya parah banget",
                        "ga layak segitu",
                        "porsinya cimit",
                        "ga sesuai ekspektasi",
                    ],
                },
        }

        if self.use_bert:
            print("Loading BERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                "indobenchmark/indobert-base-p2"
            )
            # Note: Model ini perlu di-fine-tune untuk sentiment analysis
            # Untuk sekarang, kita gunakan keyword-based approach
            print("⚠️ BERT model loaded, tapi masih menggunakan keyword-based approach")
            print("   Model perlu di-fine-tune untuk hasil optimal")

    def detect_aspect_sentiment(self, text: str, aspect: str) -> str:
        """
        Deteksi sentimen untuk aspek tertentu berdasarkan keywords.

        Args:
            text: Review text
            aspect: Nama aspek (food_quality, price, service, dll)

        Returns:
            'positive', 'negative', atau 'neutral'
        """
        text_lower = text.lower()

        if aspect not in self.aspect_keywords:
            return "neutral"

        positive_keywords = self.aspect_keywords[aspect]["positive"]
        negative_keywords = self.aspect_keywords[aspect]["negative"]

        # Hitung jumlah keyword yang muncul
        positive_count = sum(
            1 for keyword in positive_keywords if keyword in text_lower
        )
        negative_count = sum(
            1 for keyword in negative_keywords if keyword in text_lower
        )

        # Tentukan sentimen berdasarkan keyword count
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def label_single_review(self, review: str) -> Dict[str, str]:
        """
        Label satu review untuk semua aspek.

        Args:
            review: Teks review

        Returns:
            Dictionary dengan label untuk setiap aspek
        """
        labels = {}
        for aspect in self.aspects.keys():
            labels[aspect] = self.detect_aspect_sentiment(review, aspect)

        return labels

    def label_dataset(
        self, df: pd.DataFrame, review_column: str = "review"
    ) -> pd.DataFrame:
        """
        Label seluruh dataset.

        Args:
            df: DataFrame dengan kolom review
            review_column: Nama kolom yang berisi review

        Returns:
            DataFrame dengan kolom label untuk setiap aspek
        """
        print(f"Melabeli {len(df)} reviews...")

        # Buat DataFrame baru dengan kolom review
        result_df = df.copy()

        # Label setiap review
        for aspect in self.aspects.keys():
            result_df[aspect] = result_df[review_column].apply(
                lambda x: self.detect_aspect_sentiment(str(x), aspect)
            )

        # Rename kolom review menjadi sentence untuk konsistensi
        result_df = result_df.rename(columns={review_column: "sentence"})

        return result_df

    def get_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Dapatkan statistik distribusi label.

        Args:
            df: DataFrame yang sudah dilabeli

        Returns:
            DataFrame dengan statistik
        """
        stats = []

        for aspect in self.aspects.keys():
            if aspect in df.columns:
                value_counts = df[aspect].value_counts()
                stats.append(
                    {
                        "aspect": aspect,
                        "positive": value_counts.get("positive", 0),
                        "negative": value_counts.get("negative", 0),
                        "neutral": value_counts.get("neutral", 0),
                        "total": len(df),
                    }
                )

        return pd.DataFrame(stats)


def create_training_data(
    input_file: str, output_file: str, sample_size: int = None, use_bert: bool = False
):
    """
    Membuat data training dari file CSV review.

    Args:
        input_file: Path file CSV input
        output_file: Path file CSV output
        sample_size: Jumlah sample yang akan dilabeli (None = semua)
        use_bert: Gunakan BERT model untuk labeling
    """
    # Load data
    print(f"Loading data dari {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Total reviews: {len(df)}")

    # Ambil sample jika diperlukan
    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=42)
        print(f"Mengambil sample {sample_size} reviews")

    # Inisialisasi labeler
    labeler = AspectBasedSentimentLabeler(use_bert=use_bert)

    # Label dataset
    labeled_df = labeler.label_dataset(df, review_column="review")

    # Tampilkan statistik
    print("\n" + "=" * 60)
    print("STATISTIK LABEL")
    print("=" * 60)
    stats = labeler.get_statistics(labeled_df)
    print(stats.to_string(index=False))

    # Hitung persentase
    print("\n" + "=" * 60)
    print("PERSENTASE DISTRIBUSI")
    print("=" * 60)
    for aspect in labeler.aspects.keys():
        if aspect in labeled_df.columns:
            print(f"\n{aspect.upper()}:")
            value_counts = labeled_df[aspect].value_counts(normalize=True) * 100
            for label, pct in value_counts.items():
                print(f"  {label}: {pct:.2f}%")

    # Simpan hasil
    labeled_df.to_csv(output_file, index=False)
    print(f"\n✓ Data training berhasil disimpan ke: {output_file}")

    # Tampilkan sample
    print("\n" + "=" * 60)
    print("SAMPLE DATA (5 baris pertama)")
    print("=" * 60)
    print(labeled_df.head().to_string())

    return labeled_df


def manual_review_labels(input_file: str, output_file: str, start_idx: int = 0):
    """
    Review dan edit label secara manual.

    Args:
        input_file: File CSV yang sudah dilabeli
        output_file: File output setelah review
        start_idx: Index mulai review
    """
    df = pd.read_csv(input_file)

    print("=" * 60)
    print("MANUAL LABEL REVIEW")
    print("=" * 60)
    print("Instruksi:")
    print("- Tekan Enter untuk keep label")
    print("- Ketik 'p' untuk positive, 'n' untuk negative, 'neu' untuk neutral")
    print("- Ketik 'q' untuk quit dan save")
    print("=" * 60)

    aspects = ["food_quality", "price", "service", "ambiance", "portion"]

    for idx in range(start_idx, len(df)):
        print(f"\n[{idx + 1}/{len(df)}] Review:")
        print(f"'{df.loc[idx, 'sentence'][:200]}...'")
        print()

        for aspect in aspects:
            current_label = df.loc[idx, aspect]
            print(f"{aspect}: [{current_label}] ", end="")
            user_input = input().strip().lower()

            if user_input == "q":
                df.to_csv(output_file, index=False)
                print(f"\n✓ Progress disimpan ke: {output_file}")
                return
            elif user_input == "p":
                df.loc[idx, aspect] = "positive"
            elif user_input == "n":
                df.loc[idx, aspect] = "negative"
            elif user_input == "neu":
                df.loc[idx, aspect] = "neutral"
            # Jika Enter (empty), keep current label

        # Auto-save setiap 10 reviews
        if (idx + 1) % 10 == 0:
            df.to_csv(output_file, index=False)
            print(f"\n[Auto-saved at review {idx + 1}]")

    df.to_csv(output_file, index=False)
    print(f"\n✓ Semua label selesai direview. Disimpan ke: {output_file}")


# Example usage
if __name__ == "__main__":
    # Konfigurasi
    INPUT_FILE = "data_clean/all_reviews_merged.csv"
    OUTPUT_FILE = "data_training/labeled_reviews.csv"

    # Pilihan mode
    print("=" * 60)
    print("ASPECT-BASED SENTIMENT ANALYSIS - DATA LABELING")
    print("=" * 60)
    print("\nMode:")
    print("1. Auto-label semua data (keyword-based)")
    print("2. Auto-label sample data")
    print("3. Manual review labels")

    mode = input("\nPilih mode (1/2/3): ").strip()

    if mode == "1":
        # Auto-label semua data
        labeled_df = create_training_data(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            sample_size=None,
            use_bert=False,
        )

    elif mode == "2":
        # Auto-label sample
        sample_size = int(input("Jumlah sample yang ingin dilabeli: "))
        labeled_df = create_training_data(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            sample_size=sample_size,
            use_bert=False,
        )

    elif mode == "3":
        # Manual review
        labeled_file = input("Path file yang sudah dilabeli: ").strip()
        start_idx = int(input("Mulai dari index (0 untuk awal): "))
        manual_review_labels(
            input_file=labeled_file, output_file=OUTPUT_FILE, start_idx=start_idx
        )

    else:
        print("Mode tidak valid!")
