from datetime import datetime


def test_fetch_latest_create_date_of_rumor_when_exception(mocker,
                                                          rumor,
                                                          test_cdc,
                                                          test_fetch_latest_create_date_of_rumor):
    mocker.patch(
        'models.aws.ddb.rumor_model.RumorModel.source_create_date_index.query',
        return_value="exception"
    )
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_cdc.source, None)
    assert latest_create_date is None


def test_fetch_latest_create_date_of_rumor_when_no_rumor_in_DB(mocker,
                                                               rumor,
                                                               test_cdc,
                                                               test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2015-01-01"
    expected_date = datetime.strptime(expected_date_str, "%Y-%m-%d")
    mocker.patch(
        'models.aws.ddb.rumor_model.RumorModel.source_create_date_index.query',
        return_value=[]
    )
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_cdc.source, None)
    assert latest_create_date == expected_date


def test_fetch_latest_create_date_of_rumor_when_rumors_in_DB(mocker,
                                                             rumor,
                                                             test_cdc,
                                                             test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2021-01-01"
    expected_date = datetime.strptime(expected_date_str, "%Y-%m-%d")
    mocker.patch(
        'models.aws.ddb.rumor_model.RumorModel.source_create_date_index.query',
        return_value=rumor(expected_date_str)
    )
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_cdc.source, None)
    assert latest_create_date == expected_date


def test_fetch_latest_create_date_of_rumor_when_set_date(mocker,
                                                         test_cdc,
                                                         test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2021-05-01"
    expected_date = datetime.strptime(expected_date_str, "%Y-%m-%d")
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_cdc.source, expected_date_str)
    assert latest_create_date == expected_date


def test_cdc_crawler_parse_rumor_links(mocker,
                                       test_cdc,
                                       test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2021-01-01"
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_cdc.source, expected_date_str)
    pn = 1

    f = open("./tests/sample/cdc/rumor_links_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.cdc.CdcCrawler.query',
        return_value=html_content
    )

    _, rumor_infos = test_cdc.parse_rumor_links(pn, latest_create_date)
    rumor_infos = sorted(rumor_infos, key=lambda k: k['date'])

    expected_rumor_infos = [
        {
            'link': 'https://www.cdc.gov.tw/Bulletin/Detail/LLgmmeLv3tPsDU492d35wA?typeid=8772',
            'date': '2021-01-15',
            'original_title': '網傳「沒事不要去以下醫院」等不實訊息，請民眾勿轉傳以免觸法'
        },
        {
            'link': 'https://www.cdc.gov.tw/Bulletin/Detail/E54hYlJNg_rWoT-0BPSOBg?typeid=8772',
            'date': '2021-01-29',
            'original_title': '網傳「別出門，看疫情控制情況」等不實訊息，勿轉傳以免觸法'
        }
    ]
    assert rumor_infos == expected_rumor_infos


def test_cdc_crawler_parse_rumor_content(mocker,
                                         test_cdc,
                                         test_fetch_latest_create_date_of_rumor):
    test_rumor_info = {
        'link': 'https://www.cdc.gov.tw/Bulletin/Detail/E54hYlJNg_rWoT-0BPSOBg?typeid=8772',
        'date': '2021-01-29',
        'original_title': '網傳「別出門，看疫情控制情況」等不實訊息，勿轉傳以免觸法'
    }

    f = open("./tests/sample/cdc/rumor_content_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.cdc.CdcCrawler.query',
        return_value=html_content
    )

    rumor_content = test_cdc.parse_rumor_content(test_rumor_info)
    assert rumor_content['id'] is not None
    assert rumor_content['clarification'] is not None
    assert "TEST-" in rumor_content['clarification']
    assert rumor_content['create_date'] is not None
    assert rumor_content['title'] is not None
    assert rumor_content['original_title'] is not None
    assert rumor_content['rumors'] is not None
    assert rumor_content['link'] is not None
    assert rumor_content['source'] is not None


def test_fda_crawler_parse_rumor_links(mocker,
                                       test_fda,
                                       test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2021-01-01"
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_fda.source, expected_date_str)
    pn = 1

    f = open("./tests/sample/fda/rumor_links_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.fda.FdaCrawler.query',
        return_value=html_content
    )

    _, rumor_infos = test_fda.parse_rumor_links(pn, latest_create_date)
    rumor_infos = sorted(rumor_infos, key=lambda k: k['date'])
    expected_rumor_infos = [
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26744',
            'date': '2021-02-02'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26768',
            'date': '2021-02-09'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26787',
            'date': '2021-02-23'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26815',
            'date': '2021-03-02'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26828',
            'date': '2021-03-09'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26844',
            'date': '2021-03-16'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26860',
            'date': '2021-03-23'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26881',
            'date': '2021-03-30'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26908',
            'date': '2021-04-06'
        },
        {
            'link': 'https://www.fda.gov.tw/TC/TEST-newsContent.aspx?cid=5049&id=26923',
            'date': '2021-04-13'
        }
    ]
    assert rumor_infos == expected_rumor_infos


def test_fda_crawler_parse_rumor_content(mocker,
                                         test_fda,
                                         test_fetch_latest_create_date_of_rumor):
    f = open("./tests/sample/fda/rumor_content_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.fda.FdaCrawler.query',
        return_value=html_content
    )

    test_rumor_info = {
        'link': 'https://www.fda.gov.tw/TC/newsContent.aspx?cid=5049&id=26923',
        'date': '2021-04-13'
    }
    rumor_content = test_fda.parse_rumor_content(test_rumor_info)
    assert rumor_content['id'] is not None
    assert rumor_content['clarification'] is not None
    assert "TEST-" in rumor_content['clarification']
    assert rumor_content['create_date'] is not None
    assert rumor_content['title'] is not None
    assert rumor_content['original_title'] is not None
    assert rumor_content['rumors'] is not None
    assert rumor_content['link'] is not None
    assert rumor_content['source'] is not None


def test_mofa_crawler_parse_rumor_links(mocker,
                                        test_mofa,
                                        test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2021-01-01"
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_mofa.source, expected_date_str)
    pn = 1

    f = open("./tests/sample/mofa/rumor_links_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.mofa.MofaCrawler.query',
        return_value=html_content
    )

    _, rumor_infos = test_mofa.parse_rumor_links(pn, latest_create_date)
    expected_rumor_infos = [
        {
            'link': 'https://www.mofa.gov.tw/TEST-News_Content.aspx?n=1163&s=95696',
            'date': '2021-04-16'
        }
    ]
    assert rumor_infos == expected_rumor_infos


def test_mofa_crawler_parse_rumor_content(mocker,
                                          test_mofa,
                                          test_fetch_latest_create_date_of_rumor):
    test_rumor_info = {
        'link': 'https://www.mofa.gov.tw/News_Content.aspx?n=1163&s=95696',
        'date': '2021-04-16'
    }

    f = open("./tests/sample/mofa/rumor_content_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.mofa.MofaCrawler.query',
        return_value=html_content
    )

    rumor_content = test_mofa.parse_rumor_content(test_rumor_info)
    assert rumor_content['id'] is not None
    assert rumor_content['clarification'] is not None
    assert "TEST-" in rumor_content['clarification']
    assert rumor_content['create_date'] is not None
    assert rumor_content['title'] is not None
    assert rumor_content['original_title'] is not None
    assert rumor_content['rumors'] is not None
    assert rumor_content['link'] is not None
    assert rumor_content['source'] is not None


def test_tfc_crawler_parse_rumor_links(mocker,
                                       test_tfc,
                                       test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2021-04-01"
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_tfc.source, expected_date_str)
    pn = 1

    f = open("./tests/sample/tfc/rumor_links_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.tfc.TfcCrawler.query',
        return_value=html_content
    )

    _, rumor_infos = test_tfc.parse_rumor_links(pn, latest_create_date)
    rumor_infos = sorted(rumor_infos, key=lambda k: k['date'])

    expected_rumor_infos = [
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5268',
            'date': '2021-04-08',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/886_photo.png?itok=vRQO9nbf'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5267',
            'date': '2021-04-08',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/845_00.jpg?itok=yCUU53YS'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5266',
            'date': '2021-04-08',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/884_00.jpg?itok=pfithZOS'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5265',
            'date': '2021-04-08',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/883_photo.png?itok=X9vMgRPt'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5272',
            'date': '2021-04-09',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/888_00.jpg?itok=0fWnTuzw'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5269',
            'date': '2021-04-09',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/887_%E9%99%B3%E6%99%82%E4%B8%AD%E4%B8%9F%E8%87%89%E5%88%B0%E9%9F%93%E5%9C%8B.jpg?itok=tk6wUUc7'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5278',
            'date': '2021-04-12',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/890_photo_0.jpeg?itok=qVv-Up7O'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5277',
            'date': '2021-04-12',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/889_%E6%89%8B%E6%A9%9F%E9%9B%BB%E7%A3%81%E6%B3%A2.png?itok=Qh_MXovR'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/5279',
            'date': '2021-04-13',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/891_photo.jpeg?itok=BvavAULA'
        },
        {
            'link': 'https://tfc-taiwan.org.tw/articles/TEST-5283',
            'date': '2021-04-14',
            'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/892_2_0.jpg?itok=1rKFr72z'
        }
    ]
    print(rumor_infos)
    assert rumor_infos == expected_rumor_infos


def test_tfc_crawler_parse_rumor_content(mocker,
                                         test_tfc,
                                         test_fetch_latest_create_date_of_rumor):
    test_rumor_info = {
        'link': 'https://tfc-taiwan.org.tw/articles/5283',
        'date': '2021-04-14',
        'img': 'https://tfc-taiwan.org.tw/sites/default/files/styles/r1d33/public/upload/node/field_blog_images/892_2_0.jpg?itok=1rKFr72z'
    }

    f = open("./tests/sample/tfc/rumor_content_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.tfc.TfcCrawler.query',
        return_value=html_content
    )

    rumor_content = test_tfc.parse_rumor_content(test_rumor_info)
    assert rumor_content['id'] is not None
    assert rumor_content['clarification'] is not None
    assert "TEST-" in rumor_content['clarification']
    assert rumor_content['create_date'] is not None
    assert rumor_content['title'] is not None
    assert rumor_content['original_title'] is not None
    assert rumor_content['rumors'] is not None
    assert rumor_content['preface'] is not None
    assert rumor_content['tags'] is not None
    assert rumor_content['image_link'] is not None
    assert rumor_content['link'] is not None
    assert rumor_content['source'] is not None


def test_mygopen_crawler_parse_rumor_links(mocker,
                                           test_mygopen,
                                           test_fetch_latest_create_date_of_rumor):
    expected_date_str = "2021-04-01"
    latest_create_date = test_fetch_latest_create_date_of_rumor(test_mygopen.source, expected_date_str)

    f = open("./tests/sample/mygopen/rumor_links_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.mygopen.MygopenCrawler.query',
        return_value=html_content
    )

    rumor_infos = test_mygopen.parse_rumor_links(latest_create_date)
    rumor_infos = sorted(rumor_infos, key=lambda k: k['date'])

    expected_rumor_infos = [
        {
            'title': '【錯誤】台海上空發生空戰？台四架F-16戰機聯合叛逃？老謠言非近期事件',
            'link': 'https://www.mygopen.com/2021/04/f-16.html',
            'date': '2021-04-01'
        },
        {
            'title': '【查證】晚上不要運動？鍛鍊要「講時間」不然傷身？中西醫解析',
            'link': 'https://www.mygopen.com/2021/04/exercise.html',
            'date': '2021-04-02'
        },
        {
            'title': 'TEST-【誤導】突然無法小便，就舉起雙手大力跳躍就可順利排尿？醫：不建議',
            'link': 'https://www.mygopen.com/2021/04/urination.html',
            'date': '2021-04-02'
        }
    ]
    assert rumor_infos == expected_rumor_infos


def test_mygopen_crawler_parse_rumor_content(mocker,
                                             test_mygopen,
                                             test_fetch_latest_create_date_of_rumor):

    test_rumor_info = {
        'title': '【誤導】突然無法小便，就舉起雙手大力跳躍就可順利排尿？醫：不建議',
        'link': 'https://www.mygopen.com/2021/04/urination.html',
        'date': '2021-04-02'
    }

    f = open("./tests/sample/mygopen/rumor_content_html", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.mygopen.MygopenCrawler.query',
        return_value=html_content
    )
    rumor_content = test_mygopen.parse_rumor_content(test_rumor_info)
    assert rumor_content['id'] is not None
    assert rumor_content['clarification'] is not None
    assert "TEST-" in rumor_content['clarification']
    assert rumor_content['create_date'] is not None
    assert rumor_content['title'] is not None
    assert rumor_content['original_title'] is not None
    assert rumor_content['rumors'] is not None
    assert rumor_content['preface'] is not None
    assert rumor_content['tags'] is not None
    assert rumor_content['image_link'] is not None
    assert rumor_content['link'] is not None
    assert rumor_content['source'] is not None


def test_mygopen_crawler_parse_rumor_content_two_rumor(mocker,
                                                       test_mygopen,
                                                       test_fetch_latest_create_date_of_rumor):

    test_rumor_info = {
        'title': '【假訊息】手機放在廚房爆炸的影片？會產生輻射熱爆炸？謠言',
        'link': 'https://www.mygopen.com/2019/10/phone-explosion-kitchen.html',
        'date': '2019-10-25'
    }

    f = open("./tests/sample/mygopen/rumor_content_html_two_rumors", "r")
    html_content = f.read()
    mocker.patch(
        'backoffice.crawler.mygopen.MygopenCrawler.query',
        return_value=html_content
    )
    rumor_content = test_mygopen.parse_rumor_content(test_rumor_info)
    assert rumor_content['id'] is not None
    assert rumor_content['clarification'] is not None
    assert "TEST-" in rumor_content['clarification']
    assert rumor_content['create_date'] is not None
    assert rumor_content['title'] is not None
    assert rumor_content['original_title'] is not None
    assert rumor_content['rumors'] is not None
    assert len(rumor_content['rumors']) == 2
    assert rumor_content['preface'] is not None
    assert rumor_content['tags'] is not None
    assert rumor_content['image_link'] is not None
    assert rumor_content['link'] is not None
    assert rumor_content['source'] is not None
