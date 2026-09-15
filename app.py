import streamlit as st
import pandas as pd
import serpapi
import tempfile
import os

from streamlit_searchbox import st_searchbox


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Product Recommendation System",
    page_icon="🛍️",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "products_df" not in st.session_state:
    st.session_state.products_df = None

if "image_search_mode" not in st.session_state:
    st.session_state.image_search_mode = False

if "last_search_type" not in st.session_state:
    st.session_state.last_search_type = "Text Search"


# =========================================================
# SERPAPI CLIENT
# =========================================================

try:

    API_KEY = st.secrets["SERPAPI_KEY"]

    client = serpapi.Client(
        api_key=API_KEY
    )

except Exception:

    st.error(
        "SerpApi API key is not configured correctly."
    )

    st.stop()


# =========================================================
# DYNAMIC SEARCH SUGGESTIONS
# =========================================================

def product_suggestions(searchterm):

    searchterm = searchterm.strip()

    if not searchterm:
        return []

    try:

        results = client.search({

            "engine": "google_autocomplete",

            "q": searchterm,

            "gl": "in",

            "hl": "en"

        })

        suggestions = results.get(
            "suggestions",
            []
        )

        return [

            suggestion.get(
                "value"
            )

            for suggestion in suggestions

            if suggestion.get("value")

        ]

    except Exception:

        return []


# =========================================================
# TEXT PRODUCT SEARCH
# =========================================================

def search_products(query):

    query = query.strip()

    if not query:
        return pd.DataFrame()

    results = client.search({

        "engine": "google_shopping",

        "q": query,

        "gl": "in",

        "hl": "en"

    })

    products = results.get(
        "shopping_results",
        []
    )

    data = []

    for product in products:

        product_link = product.get(
            "product_link",
            ""
        )

        data.append({

            "title": product.get(
                "title",
                "N/A"
            ),

            "price": product.get(
                "price",
                "N/A"
            ),

            "rating": product.get(
                "rating",
                "N/A"
            ),

            "reviews": product.get(
                "reviews",
                "N/A"
            ),

            "source": product.get(
                "source",
                "N/A"
            ),

            "image": product.get(
                "thumbnail",
                ""
            ),

            "link": product_link

        })

    return pd.DataFrame(data)


# =========================================================
# IMAGE SEARCH
# =========================================================

def image_search(image_path):

    image_result = client.upload_image(
        image_path
    )

    image_id = image_result.get(
        "image_id"
    )

    if not image_id:

        raise Exception(
            "Could not upload image to SerpApi."
        )

    lens_results = client.search({

        "engine": "google_lens",

        "image_id": image_id,

        "type": "products",

        "hl": "en",

        "country": "in"

    })

    products_lens = lens_results.get(
        "visual_matches",
        []
    )

    visual_products = []

    for product in products_lens:

        price = product.get(
            "price"
        )

        if isinstance(
            price,
            dict
        ):

            price = price.get(
                "value"
            )

        visual_products.append({

            "title": product.get(
                "title",
                "Product"
            ),

            "price": price,

            "rating": product.get(
                "rating"
            ),

            "reviews": product.get(
                "reviews"
            ),

            "source": product.get(
                "source"
            ),

            "image": product.get(
                "thumbnail"
            ),

            "link": product.get("link") or product.get("product_link", "")

        })

    return pd.DataFrame(
        visual_products
    )


# =========================================================
# DISPLAY PRODUCTS
# =========================================================

def display_products(
    df,
    image_search_mode=False
):

    if df is None or df.empty:

        st.warning(
            "No products found."
        )

        return

    df = df.copy()


    # -----------------------------------------------------
    # PRICE CONVERSION
    # -----------------------------------------------------

    df["price_numeric"] = (

        df["price"]
        .astype(str)
        .str.replace(
            r"[^\d.]",
            "",
            regex=True
        )

    )

    df["price_numeric"] = pd.to_numeric(

        df["price_numeric"],

        errors="coerce"

    )


    # -----------------------------------------------------
    # RATING CONVERSION
    # -----------------------------------------------------

    df["rating_numeric"] = pd.to_numeric(

        df["rating"],

        errors="coerce"

    )


    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    filter_col1, filter_col2 = st.columns(2)


    with filter_col1:

        max_price = st.number_input(

            "💰 Maximum Price",

            min_value=0.0,

            max_value=100000.0,

            value=100000.0,

            step=500.0,

            key=(

                "image_max_price"

                if image_search_mode

                else "text_max_price"

            )

        )


    with filter_col2:

        min_rating = st.slider(

            "⭐ Minimum Rating",

            min_value=0.0,

            max_value=5.0,

            value=0.0,

            step=0.5,

            key=(

                "image_min_rating"

                if image_search_mode

                else "text_min_rating"

            )

        )


    # -----------------------------------------------------
    # APPLY PRICE FILTER
    # -----------------------------------------------------

    if max_price < 100000:

        df = df[

            (

                df["price_numeric"]
                <= max_price

            )

            |

            (

                df["price_numeric"]
                .isna()

            )

        ]


    # -----------------------------------------------------
    # APPLY RATING FILTER
    # -----------------------------------------------------

    if min_rating > 0:

        df = df[

            (

                df["rating_numeric"]
                >= min_rating

            )

            |

            (

                df["rating_numeric"]
                .isna()

            )

        ]


    if df.empty:

        st.warning(
            "No products match the selected filters."
        )

        return


    # -----------------------------------------------------
    # RESULT COUNT
    # -----------------------------------------------------

    st.subheader(
        f"🛍️ {len(df)} products found"
    )


    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

    sort_option = st.selectbox(

        "🔽 Sort Products",

        [

            "Sort",

            "Price: Low to High",

            "Price: High to Low",

            "Rating: High to Low"

        ],

        key=(

            "image_sort"

            if image_search_mode

            else "text_sort"

        )

    )


    if sort_option == "Price: Low to High":

        df = df.sort_values(

            by="price_numeric",

            ascending=True,

            na_position="last"

        )


    elif sort_option == "Price: High to Low":

        df = df.sort_values(

            by="price_numeric",

            ascending=False,

            na_position="last"

        )


    elif sort_option == "Rating: High to Low":

        df = df.sort_values(

            by="rating_numeric",

            ascending=False,

            na_position="last"

        )


    # -----------------------------------------------------
    # PRODUCT CARDS
    # -----------------------------------------------------

    cols = st.columns(4)


    for i, (_, product) in enumerate(
        df.iterrows()
    ):

        with cols[i % 4]:

            image = product.get(
                "image"
            )

            title = product.get(
                "title"
            )

            price = product.get(
                "price"
            )

            rating = product.get(
                "rating"
            )

            reviews = product.get(
                "reviews"
            )

            source = product.get(
                "source"
            )

            link = product.get(
                "link"
            )


            if not title:

                title = "Product"


            if not price:

                price = "Price unavailable"


            if not source:

                source = "Seller unavailable"


            if pd.notna(rating):

                rating_text = (
                    f"⭐ {rating}"
                )

            else:

                rating_text = "⭐ N/A"


            if pd.notna(reviews):

                try:

                    reviews_text = (
                        f"{int(reviews)} reviews"
                    )

                except:

                    reviews_text = (
                        f"{reviews} reviews"
                    )

            else:

                reviews_text = (
                    "No reviews"
                )


            with st.container(
                border=True
            ):

                if image:

                    st.image(

                        image,

                        use_container_width=True

                    )


                st.markdown(
                    f"**{title[:60]}**"
                )


                st.markdown(
                    f"💰 **{price}**"
                )


                st.write(

                    f"{rating_text}  |  "
                    f"{reviews_text}"

                )


                st.caption(
                    f"🏪 {source}"
                )


                st.link_button(

                    "🛒 View Product",

                    link,

                    use_container_width=True

                )


# =========================================================
# PAGE TITLE
# =========================================================

st.title(
    "🛍️ Product Recommendation System"
)

st.write(
    "Search for products using text or upload a product image."
)


# =========================================================
# SEARCH TYPE
# =========================================================

search_type = st.radio(

    "Choose search method:",

    [

        "Text Search",

        "Image Search"

    ],

    horizontal=True

)


# =========================================================
# CLEAR OLD RESULTS WHEN SEARCH TYPE CHANGES
# =========================================================

if (

    st.session_state.last_search_type
    != search_type

):

    st.session_state.products_df = None

    st.session_state.image_search_mode = False

    st.session_state.last_search_type = (
        search_type
    )


st.divider()


# =========================================================
# TEXT SEARCH
# =========================================================

if search_type == "Text Search":

    st.subheader(
        "🔎 Search Products"
    )


    # -----------------------------------------------------
    # DYNAMIC SEARCH BOX
    # -----------------------------------------------------

    search_query = st_searchbox(

        product_suggestions,

        placeholder="Search for any product...",

        label=None,

        key="text_search_query",

        debounce=300,

        default_use_searchterm=True,

        edit_after_submit="option"

    )


    # -----------------------------------------------------
    # SEARCH BUTTON
    # -----------------------------------------------------

    search_clicked = st.button(

        "🔎 Search Products",

        type="primary",

        use_container_width=True

    )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search_clicked:

        if not search_query:

            st.warning(
                "Please enter a product name."
            )

        else:

            with st.spinner(
                "Searching for products..."
            ):

                try:

                    products_df = search_products(
                        search_query
                    )


                    if products_df.empty:

                        st.warning(
                            "No products were returned by SerpApi."
                        )

                    else:

                        st.session_state.products_df = (
                            products_df
                        )

                        st.session_state.image_search_mode = (
                            False
                        )


                except Exception as e:

                    st.error(
                        f"Search failed: {e}"
                    )


    # -----------------------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------------------

    if (

        st.session_state.products_df
        is not None

        and not st.session_state.products_df.empty

        and st.session_state.image_search_mode
        == False

    ):

        display_products(

            st.session_state.products_df,

            image_search_mode=False

        )


        # -------------------------------------------------
        # CLEAR RESULTS
        # -------------------------------------------------

        if st.button(

            "🗑️ Clear Results",

            key="clear_text_results"

        ):

            st.session_state.products_df = None

            st.rerun()


# =========================================================
# IMAGE SEARCH
# =========================================================

elif search_type == "Image Search":

    st.subheader(
        "📷 Search Using Product Image"
    )


    uploaded_file = st.file_uploader(

        "📷 Upload a product image",

        type=[

            "jpg",
            "jpeg",
            "png",
            "webp"

        ],

        key="product_image"

    )


    if uploaded_file:

        st.subheader(
            "📷 Uploaded Product"
        )


        st.image(

            uploaded_file,

            caption="Image you uploaded",

            width=300

        )


        if st.button(

            "🔍 Find Similar Products",

            type="primary",

            key="find_similar_products"

        ):

            file_extension = os.path.splitext(

                uploaded_file.name

            )[1]


            with tempfile.NamedTemporaryFile(

                delete=False,

                suffix=file_extension

            ) as temp_file:

                temp_file.write(

                    uploaded_file.getbuffer()

                )

                temp_image_path = (
                    temp_file.name
                )


            try:

                with st.spinner(
                    "Finding similar products..."
                ):

                    products_df = image_search(
                        temp_image_path
                    )


                if products_df.empty:

                    st.warning(
                        "No similar products found."
                    )

                else:

                    products_df = (

                        products_df
                        .head(10)

                    )


                    st.session_state.products_df = (
                        products_df
                    )

                    st.session_state.image_search_mode = (
                        True
                    )


            except Exception as e:

                st.error(
                    f"Image search failed: {e}"
                )


            finally:

                if os.path.exists(
                    temp_image_path
                ):

                    os.remove(
                        temp_image_path
                    )


        # -------------------------------------------------
        # DISPLAY IMAGE RESULTS
        # -------------------------------------------------

        if (

            st.session_state.products_df
            is not None

            and not st.session_state.products_df.empty

            and st.session_state.image_search_mode
            == True

        ):

            display_products(

                st.session_state.products_df,

                image_search_mode=True

            )


            # ---------------------------------------------
            # CLEAR RESULTS
            # ---------------------------------------------

            if st.button(

                "🗑️ Clear Results",

                key="clear_image_results"

            ):

                st.session_state.products_df = None

                st.rerun()
