from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.models import (TemplateSendMessage)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuArea,
    RichMenuSize,
    RichMenuBatchRequest,
    RichMenuBounds,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    LocationMessage,
    FlexContainer,
    QuickReply,
    QuickReplyItem,
    FlexBubble,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    LocationAction,
    URIAction,
    CarouselColumn,
    CarouselTemplate,
    MessageAction,
    PushMessageRequest,
    BroadcastRequest,
    MulticastRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    PostbackEvent,
    LocationMessageContent,
    TextMessageContent,

)
from dotenv import load_dotenv
import requests
import json
import os
import random
# 導入部落格爬蟲

import blogdata
from bs4 import BeautifulSoup


load_dotenv()

# 使用getenv取得環境變數
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# 創建flask框架應用程序
app = Flask(__name__)
# 設定Token跟Channel secret
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
# 存選擇條件

user_filters = {}
user_filters_restaurant = {}
user_location = {}

# 確保只有來自 LINE 平台的有效請求才能觸發對應的處理邏輯


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'
# 加入好友 發歡迎圖及選項


@handler.add(FollowEvent)
def handle_follow(event):
    line_flex_json = {
        "type": "bubble",
        "size": "kilo",
        "hero": {
            "type": "image",
            "url": "https://i.imgur.com/guTgQBc.jpeg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "align": "center"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "歡迎使用今天要吃啥，在這裡你可以：",
                    "weight": "bold",
                    "size": "sm",
                    "margin": "sm",
                    "style": "normal",
                    "decoration": "none",
                    "position": "relative",
                    "gravity": "center",
                    "wrap": True,
                    "offsetTop": "none",
                    "offsetBottom": "xs",
                    "align": "start"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "1️⃣ 查詢部落客精選台北美食",
                        "data": "action=search_blog"
                    },
                    "margin": "none",
                    "gravity": "top"
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "2️⃣ 尋找附近美食",
                        "data": "action=find_nearby"
                    },
                    "margin": "md"
                }
            ],
            "flex": 0,
            "alignItems": "center"
        }
    }
    line_str = json.dumps(line_flex_json)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[FlexMessage(
                    alt_text="Follow Event",
                    contents=FlexContainer.from_json(line_str)
                )])
        )

# -------------------------------------------------------------------

# 第二階段-讓user選擇2大功能


@handler.add(PostbackEvent)
def handle_post_back_richmenu(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        postback_data = event.postback.data
        user_id = event.source.user_id
        if postback_data == "action=search_blog":  # 選擇精選美食，跳出區域
            quickreply = QuickReply(
                items=[
                    QuickReplyItem(action=PostbackAction
                                   (label='大安區',
                                    data='district=大安區',
                                    displayText='大安區',)),
                    QuickReplyItem(action=PostbackAction
                                   (label='南港區',
                                    data='district=南港區',
                                    displayText='南港區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='信義區',
                                    data='district=信義區',
                                    displayText='信義區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='萬華區',
                                    data='district=萬華區',
                                    displayText='萬華區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='內湖區',
                                    data='district=內湖區',
                                    displayText='內湖區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='松山區',
                                    data='district=松山區',
                                    displayText='松山區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='中山區',
                                    data='district=中山區',
                                    displayText='中山區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='士林區',
                                    data='district=士林區',
                                    displayText='士林區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='北投區',
                                    data='district=北投區',
                                    displayText='北投區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='文山區',
                                    data='district=文山區',
                                    displayText='文山區')),
                    QuickReplyItem(action=PostbackAction
                                   (label='大同區',
                                    data='district=大同區',
                                    displayText='大同區')),
                ])
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇想查詢的區域:",
                        quickReply=quickreply
                    )]))

        elif postback_data == "action=find_nearby":  # 選擇附近美食，跳兩選項
            quickreply = QuickReply(
                items=[
                    QuickReplyItem(action=PostbackAction
                                   (label='🍴馬上吃',
                                    data='rightnow',
                                    displayText='🍴馬上吃')),
                    QuickReplyItem(action=PostbackAction
                                   (label='📅預定',
                                    data='reserve',
                                    displayText='📅預定'))
                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇偏好模式：",
                        quick_reply=quickreply
                    )]))

        # 部落格路徑-回傳文章
        if postback_data == 'district=大安區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/347436'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/347436')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=南港區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/347590'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/347590')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=信義區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/346434'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/346434')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=萬華區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/342091'),
                text='N精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/342091')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=內湖區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/346730'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/346730')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=松山區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/347158'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/347158')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=中山區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/347502'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/347502')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=士林區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/349426'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/349426')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=北投區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/339688'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/339688')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=文山區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/347192'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/347192')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))
        elif postback_data == 'district=大同區':
            url = 'https://i.imgur.com/tGVbBdn.png'
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title=blogdata.crawl_random_title(
                    'https://supertaste.tvbs.com.tw/pack/347630'),
                text='精選美食٩(๑❛ᴗ❛๑)۶',
                actions=[
                    URIAction(label='查看文章',
                              uri='https://supertaste.tvbs.com.tw/pack/347630')
                ])
            template_message = TemplateMessage(
                alt_text="文章連結按鈕",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]))

        # 選擇找附近功能-讓使用者篩選評論數
        if postback_data == 'rightnow' or postback_data == 'reserve':
            user_filters[user_id] = {"type": postback_data}
            quickReply = QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(
                            label="評論數 > 100",
                            data="reviews_100",
                            displayText="評論數 > 100"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="評論數 > 300",
                            data="reviews_300",
                            displayText="評論數 > 300"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="評論數 > 500",
                            data="reviews_500",
                            displayText="評論數 > 500"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="評論數 > 700",
                            data="reviews_700",
                            displayText="評論數 > 700"
                        )
                    ),
                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇評論數條件：",
                        quickReply=quickReply
                    )]
                )
            )

        # 讓使用者篩選星等
        if postback_data.startswith("reviews_"):
            user_filters[user_id]["reviews"] = float(
                postback_data.split("_")[1])
            quickReply = QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(
                            label="星等 > 3.5",
                            data="rating_3.5",
                            displayText="星等 > 3.5"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="星等 > 4",
                            data="rating_4",
                            displayText="星等 > 4"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="星等 > 4.5",
                            data="rating_4.5",
                            displayText="星等 > 4.5"
                        )
                    )
                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇最低星等要求：",
                        quick_reply=quickReply
                    )]
                )
            )

        # 讓使用者篩選距離
        if postback_data.startswith("rating_"):
            user_filters[user_id]["rating"] = float(
                postback_data.split("_")[1])
            quickReply = QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(
                            label="半徑 500 公尺",
                            data="radius_500",
                            displayText="半徑 500 公尺"
                        )
                    ),
                    QuickReplyItem(
                        action=PostbackAction(
                            label="半徑 1000 公尺",
                            data="radius_1000",
                            displayText="半徑 1000 公尺"
                        )
                    )
                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇搜尋半徑：",
                        quick_reply=quickReply
                    )]
                )
            )

        # 讓使用者分享位置訊息
        if postback_data.startswith("radius_"):
            user_filters[user_id]["radius"] = int(postback_data.split("_")[1])
            quickreply = QuickReply(
                items=[QuickReplyItem(action=LocationAction(label='我的所在地', data='share_location'))])
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請分享你的位置資訊",
                        quickReply=quickreply
                    )]))


# 串接google api抓取餐廳資訊
@handler.add(MessageEvent)
def handle_location(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id

        filters = user_filters.get(user_id, {})
        radius = filters.get("radius")
        min_reviews = filters.get("reviews")
        min_rating = filters.get("rating")
        is_eat_now = filters.get("type") == "rightnow"

        if isinstance(event.message, LocationMessageContent):
            # 確保 user_id 對應的子字典存在
            if user_id not in user_location:
                user_location[user_id] = {}
            location = event.message
            latitude = location.latitude
            longitude = location.longitude
            user_location[user_id]["latitude"] = float(latitude)
            user_location[user_id]["longitude"] = float(longitude)
            message_text = None
        else:
            message_text = getattr(event.message, 'text',
                                   'No text attribute available')
        latitude = user_location[user_id]["latitude"]
        longitude = user_location[user_id]["longitude"]

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude}, {longitude}",
        "radius": radius,
        "type": "restaurant",
        "key": GOOGLE_API_KEY,
        "language": "zh-TW"
    }

    # 需重新設定篩選條件時才會觸發-評論數
    if message_text == "重新調整條件":
        quickReply = QuickReply(
            items=[
                QuickReplyItem(
                    action=PostbackAction(
                        label="評論數 > 100",
                        data="reviews_100",
                        displayText="評論數 > 100"
                    )
                ),
                QuickReplyItem(
                    action=PostbackAction(
                        label="評論數 > 300",
                        data="reviews_300",
                        displayText="評論數 > 300"
                    )
                ),
                QuickReplyItem(
                    action=PostbackAction(
                        label="評論數 > 500",
                        data="reviews_500",
                        displayText="評論數 > 500"
                    )
                ),
                QuickReplyItem(
                    action=PostbackAction(
                        label="評論數 > 700",
                        data="reviews_700",
                        displayText="評論數 > 700"
                    )
                )
            ]
        )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(
                    text="請重新選擇評論數條件：",
                    quick_reply=quickReply
                )]
            )
        )

    if is_eat_now:
        params["opennow"] = True
        response = requests.get(url, params=params)

    response = requests.get(url, params=params)

    # 確認請求是否成功
    if response.status_code == 200:
        results = response.json().get("results", [])

        # 將用戶設定的條件進行篩選
        filtered_restaurants = []
        for restaurant in results:
            if restaurant.get("user_ratings_total", 0) >= min_reviews and restaurant.get("rating", 0) >= min_rating:
                filtered_restaurants.append(restaurant)

        # 清理不需要的資訊
        cleaned_restaurants = []
        for restaurant in filtered_restaurants:
            cleaned_restaurant = {
                "name": restaurant.get("name"),
                "photos": restaurant.get("photos", []),
                "place_id": restaurant.get("place_id"),
                "price_level": restaurant.get("price_level"),
                "rating": restaurant.get("rating"),
                "types": restaurant.get("types"),
                "user_ratings_total": restaurant.get("user_ratings_total"),
                "vicinity": restaurant.get("vicinity"),
                "restaurant_latitude": restaurant.get("geometry", {}).get("location", {}).get("lat"),
                "restaurant_longitude": restaurant.get("geometry", {}).get("location", {}).get("lng")
            }
            cleaned_restaurants.append(cleaned_restaurant)

        restaurants_amount = len(cleaned_restaurants)

        # 將回傳內容接到模板上...
        def create_carousel_template(selected_restaurants, api_key):
            carousel_columns = []
            for restaurant in selected_restaurants:
                name = restaurant["name"]
                # 將大於30字元的餐廳的標題縮短至小於10字元 依面板顯示結果調整
                name = name[:10] + "..." if len(name) > 30 else name
                address = restaurant["vicinity"]
                rating = restaurant.get("rating", "無評分")
                photos = restaurant.get("photos", [])
                restaurant_latitude = restaurant["restaurant_latitude"]
                restaurant_longitude = restaurant["restaurant_longitude"]
                place_id = restaurant["place_id"]
                price_level = restaurant.get("price_level", "無價格區間")

                if photos:
                    # 如果有照片取第一張生成url
                    photo_reference = photos[0].get("photo_reference")
                    photo_width = photos[0].get("width")
                    thumbnail_image_url = f"https://maps.googleapis.com/maps/api/place/photo?key={api_key}&photoreference={photo_reference}&maxwidth={photo_width}"
                else:
                    thumbnail_image_url = None

                # 幫user導到 google map

                actions = [
                    URIAction(label="查看地圖",
                              uri=f"https://www.google.com/maps/search/?api=1&query={restaurant_latitude}%2C{restaurant_longitude}&query_place_id={place_id}"
                              )

                ]

                price = 0
                if price_level == None:
                    price = '資料不足'
                else:
                    if price_level == 1:
                        price = '$'
                    elif price_level == 2:
                        price = '$$'
                    elif price_level == 3:
                        price = '$$$'
                    elif price_level == 4:
                        price = '$$$$'

                # 建立輪播模版
                column = CarouselColumn(
                    thumbnail_image_url=thumbnail_image_url,
                    title=name,
                    text=f"星等：{rating}★\n價格區間：{price}\n地址：{address}",
                    actions=actions
                )

                # 修剪超長文字
                if len(column.text) > 60:
                    column.text = column.text[:57] + "..."  # 加上 "..." 以指示被截斷

                carousel_columns.append(column)

            carousel_template = CarouselTemplate(columns=carousel_columns)
            return carousel_template

        #  使用者滿意結果 回傳感謝文字
        if message_text == "滿意結果":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='太好了！謝謝你的使用！٩(●ᴗ●)۶')]))

        # 需要重新生成更多餐廳結果才會觸發
        elif message_text == "重新生成結果":
            user_data = user_filters_restaurant.get(user_id, {})
            remain_restaurants = user_data.get("remain_restaurants", [])
            selected_restaurants = user_data.get("selected_restaurants", [])

            if len(remain_restaurants) > 5:
                new_selected = random.sample(remain_restaurants, 5)
                user_filters_restaurant[user_id]["selected_restaurants"].extend(
                    new_selected)
                user_filters_restaurant[user_id]["remain_restaurants"] = [
                    r for r in remain_restaurants if r not in new_selected]

                # 輪播模版
                carousel_template = create_carousel_template(
                    new_selected, GOOGLE_API_KEY)
                # 建立 TemplateSendMessage
                carousel_message = TemplateMessage(
                    alt_text="餐廳", template=carousel_template)

                # 詢問滿意或重新生成
                quickReply = QuickReply(
                    items=[
                        QuickReplyItem(
                            action=MessageAction(
                                label="滿意結果",
                                text="滿意結果"
                            )
                        ),
                        QuickReplyItem(
                            action=MessageAction(
                                label="重新生成結果",
                                text="重新生成結果"
                            )
                        )
                    ]
                )
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        # messages=[carousel_message_dict]
                        messages=[carousel_message, TextMessage(
                            text='是否滿意結果？', quick_reply=quickReply)]
                    )
                )

            elif 0 < len(remain_restaurants) <= 5:
                remain_restaurants = user_filters_restaurant[user_id]["remain_restaurants"]
                selected = random.sample(
                    remain_restaurants, len(remain_restaurants))

                # 輪播模版
                carousel_template = create_carousel_template(
                    selected, GOOGLE_API_KEY)
                # 建立 TemplateSendMessage
                carousel_message = TemplateMessage(
                    alt_text="餐廳", template=carousel_template)
                # carousel_message_dict = carousel_message.as_json_dict()

                # 詢問滿意或重新生成
                quickReply = QuickReply(
                    items=[
                        QuickReplyItem(
                            action=MessageAction(
                                label="滿意結果",
                                text="滿意結果"
                            )
                        ),
                        QuickReplyItem(
                            action=MessageAction(
                                label="無更多餐廳，請重新選擇條件",
                                text="重新調整條件"
                            )
                        )
                    ]
                )
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        # messages=[carousel_message_dict]
                        messages=[carousel_message, TextMessage(
                            text='是否滿意結果？', quick_reply=quickReply)]
                    )
                )

                user_filters_restaurant[user_id]["remain_restaurants"] = []

            elif len(remain_restaurants) == 0:
                quickReply = QuickReply(
                    items=[
                        QuickReplyItem(
                            action=MessageAction(
                                label="重新調整條件",
                                text="重新調整條件"
                            )
                        )
                    ]
                )
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text="目前無更多符合條件的餐廳，請重新選擇條件。",
                            quick_reply=quickReply
                        )]
                    )
                )

        # 如果餐廳數量大於（含）五間，即隨機生成結果
        if restaurants_amount >= 5 and message_text == None:
            selected_restaurants = random.sample(cleaned_restaurants, 5)
            remain_restaurants = [
                r for r in cleaned_restaurants if r not in selected_restaurants]

            user_filters_restaurant[user_id] = {
                "selected_restaurants": selected_restaurants,
                "remain_restaurants": remain_restaurants
            }

            # 輪播模版
            carousel_template = create_carousel_template(
                selected_restaurants, GOOGLE_API_KEY)
            # 建立 TemplateSendMessage
            carousel_message = TemplateMessage(
                alt_text="餐廳", template=carousel_template)

            # 詢問滿意或重新生成
            quickReply = QuickReply(
                items=[
                    QuickReplyItem(
                        action=MessageAction(
                            label="滿意結果",
                            text="滿意結果"
                        )
                    ),
                    QuickReplyItem(
                        action=MessageAction(
                            label="重新生成結果",
                            text="重新生成結果"
                        )
                    )
                ]
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    # messages=[carousel_message_dict]
                    messages=[carousel_message, TextMessage(
                        text='是否滿意結果？', quick_reply=quickReply)]
                )
            )

        # 若餐廳結果小於五間，即要求用戶重新調整條件
        elif restaurants_amount < 5 and message_text == None:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)

                quickReply = QuickReply(
                    items=[
                        QuickReplyItem(
                            action=MessageAction(
                                label="重新調整條件",
                                text="重新調整條件"
                            )
                        )
                    ]
                )
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(
                            text="找不到符合條件的餐廳，請重新調整條件。",
                            quick_reply=quickReply
                        )]
                    )
                )


# 已加好友，顯示功能選單
def rich_menu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        messaging_api_blob = MessagingApiBlob(api_client)
        # create menu
        headers = {
            'Authorization': 'Bearer ' + CHANNEL_ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
        body = {
            "size": {
                "width": 2500,
                "height": 843
            },
            "selected": True,
            "name": "圖文選單 1",
            "chatBarText": "查看更多資訊",
            "areas": [
                {
                    "bounds": {
                        "x": 0,
                        "y": 0,
                        "width": 1250,
                        "height": 836
                    },
                    "action": {
                        "type": "postback",
                        "text": "部落客精選台北美食",
                        "data": "action=search_blog"
                    }
                },
                {
                    "bounds": {
                        "x": 1263,
                        "y": 8,
                        "width": 1237,
                        "height": 820
                    },
                    "action": {
                        "type": "postback",
                        "text": "尋找附近餐廳",
                        "data": "action=find_nearby"
                    }
                }
            ]
        }
        response = requests.post('https://api.line.me/v2/bot/richmenu',
                                 headers=headers, data=json.dumps(body).encode('utf-8'))
        response = response.json()
        rich_menu_id = response['richMenuId']
        # upload
        os.chdir(os.path.dirname(__file__))
        with open('menuphoto.png', 'rb') as image:

            # 使用新的 API 上傳圖片
            messaging_api_blob.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/png'}
            )
        line_bot_api.set_default_rich_menu(rich_menu_id)


rich_menu()


if __name__ == "__main__":
    app.run()
