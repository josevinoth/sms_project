PGDMP     4            	        z            asset_mgt_016    14.4    14.4 m   Y           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            Z           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            [           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            \           1262    43459    asset_mgt_016    DATABASE     i   CREATE DATABASE asset_mgt_016 WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'English_India.1252';
    DROP DATABASE asset_mgt_016;
                postgres    false            �            1259    43486 
   auth_group    TABLE     f   CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);
    DROP TABLE public.auth_group;
       public         heap    postgres    false            �            1259    43485    auth_group_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.auth_group_id_seq;
       public          postgres    false    216            ]           0    0    auth_group_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;
          public          postgres    false    215            �            1259    43495    auth_group_permissions    TABLE     �   CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);
 *   DROP TABLE public.auth_group_permissions;
       public         heap    postgres    false            �            1259    43494    auth_group_permissions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.auth_group_permissions_id_seq;
       public          postgres    false    218            ^           0    0    auth_group_permissions_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;
          public          postgres    false    217            �            1259    43479    auth_permission    TABLE     �   CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);
 #   DROP TABLE public.auth_permission;
       public         heap    postgres    false            �            1259    43478    auth_permission_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.auth_permission_id_seq;
       public          postgres    false    214            _           0    0    auth_permission_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;
          public          postgres    false    213            �            1259    43502 	   auth_user    TABLE     �  CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);
    DROP TABLE public.auth_user;
       public         heap    postgres    false            �            1259    43511    auth_user_groups    TABLE     ~   CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);
 $   DROP TABLE public.auth_user_groups;
       public         heap    postgres    false            �            1259    43510    auth_user_groups_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.auth_user_groups_id_seq;
       public          postgres    false    222            `           0    0    auth_user_groups_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;
          public          postgres    false    221            �            1259    43501    auth_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.auth_user_id_seq;
       public          postgres    false    220            a           0    0    auth_user_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;
          public          postgres    false    219            �            1259    43518    auth_user_user_permissions    TABLE     �   CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);
 .   DROP TABLE public.auth_user_user_permissions;
       public         heap    postgres    false            �            1259    43517 !   auth_user_user_permissions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.auth_user_user_permissions_id_seq;
       public          postgres    false    224            b           0    0 !   auth_user_user_permissions_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;
          public          postgres    false    223            �            1259    43577    django_admin_log    TABLE     �  CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);
 $   DROP TABLE public.django_admin_log;
       public         heap    postgres    false            �            1259    43576    django_admin_log_id_seq    SEQUENCE     �   CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.django_admin_log_id_seq;
       public          postgres    false    226            c           0    0    django_admin_log_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;
          public          postgres    false    225            �            1259    43470    django_content_type    TABLE     �   CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);
 '   DROP TABLE public.django_content_type;
       public         heap    postgres    false            �            1259    43469    django_content_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.django_content_type_id_seq;
       public          postgres    false    212            d           0    0    django_content_type_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;
          public          postgres    false    211            �            1259    43461    django_migrations    TABLE     �   CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);
 %   DROP TABLE public.django_migrations;
       public         heap    postgres    false            �            1259    43460    django_migrations_id_seq    SEQUENCE     �   CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.django_migrations_id_seq;
       public          postgres    false    210            e           0    0    django_migrations_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;
          public          postgres    false    209            �            1259    43606    django_session    TABLE     �   CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);
 "   DROP TABLE public.django_session;
       public         heap    postgres    false            u           1259    45139    sms_app_activeinactiveinfo    TABLE     w   CREATE TABLE public.sms_app_activeinactiveinfo (
    id bigint NOT NULL,
    active_inactive character varying(100)
);
 .   DROP TABLE public.sms_app_activeinactiveinfo;
       public         heap    postgres    false            t           1259    45138 !   sms_app_activeinactiveinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_activeinactiveinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.sms_app_activeinactiveinfo_id_seq;
       public          postgres    false    373            f           0    0 !   sms_app_activeinactiveinfo_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.sms_app_activeinactiveinfo_id_seq OWNED BY public.sms_app_activeinactiveinfo.id;
          public          postgres    false    372            �            1259    43616    sms_app_assetinfo    TABLE     �  CREATE TABLE public.sms_app_assetinfo (
    id bigint NOT NULL,
    asset_number character varying(10) NOT NULL,
    asset_model character varying(30) NOT NULL,
    asset_make character varying(30) NOT NULL,
    asset_serial_num1 character varying(10) NOT NULL,
    asset_assignedon character varying(30),
    asset_cost numeric(10,2) NOT NULL,
    asset_order_number character varying(30),
    asset_purchase_date date NOT NULL,
    asset_assignedto_id integer NOT NULL,
    asset_insurance_details_id bigint NOT NULL,
    asset_location_id bigint NOT NULL,
    asset_product_id bigint NOT NULL,
    asset_unit_id bigint NOT NULL,
    asset_vendor_id bigint NOT NULL
);
 %   DROP TABLE public.sms_app_assetinfo;
       public         heap    postgres    false            �            1259    43615    sms_app_assetinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_assetinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.sms_app_assetinfo_id_seq;
       public          postgres    false    229            g           0    0    sms_app_assetinfo_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.sms_app_assetinfo_id_seq OWNED BY public.sms_app_assetinfo.id;
          public          postgres    false    228            i           1259    44158    sms_app_assign_asset_info    TABLE       CREATE TABLE public.sms_app_assign_asset_info (
    id bigint NOT NULL,
    "AA_assingedto" character varying(20),
    "AA_assignedon" character varying(20),
    "AA_assignedby" character varying(20),
    "AA_remarks" character varying(50),
    "AA_asset_number_id" bigint
);
 -   DROP TABLE public.sms_app_assign_asset_info;
       public         heap    postgres    false            h           1259    44157     sms_app_assign_asset_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_assign_asset_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_assign_asset_info_id_seq;
       public          postgres    false    361            h           0    0     sms_app_assign_asset_info_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_assign_asset_info_id_seq OWNED BY public.sms_app_assign_asset_info.id;
          public          postgres    false    360            �            1259    43623    sms_app_axletypeinfo    TABLE     m   CREATE TABLE public.sms_app_axletypeinfo (
    id bigint NOT NULL,
    at_axletype character varying(100)
);
 (   DROP TABLE public.sms_app_axletypeinfo;
       public         heap    postgres    false            �            1259    43622    sms_app_axletypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_axletypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_axletypeinfo_id_seq;
       public          postgres    false    231            i           0    0    sms_app_axletypeinfo_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_axletypeinfo_id_seq OWNED BY public.sms_app_axletypeinfo.id;
          public          postgres    false    230            �            1259    43630    sms_app_bayinfo    TABLE     �   CREATE TABLE public.sms_app_bayinfo (
    id bigint NOT NULL,
    bay_bayname character varying(100) NOT NULL,
    "Bay_unit_name_id" bigint NOT NULL,
    bay_branch_name_id bigint NOT NULL
);
 #   DROP TABLE public.sms_app_bayinfo;
       public         heap    postgres    false            �            1259    43629    sms_app_bayinfo_id_seq    SEQUENCE        CREATE SEQUENCE public.sms_app_bayinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.sms_app_bayinfo_id_seq;
       public          postgres    false    233            j           0    0    sms_app_bayinfo_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.sms_app_bayinfo_id_seq OWNED BY public.sms_app_bayinfo.id;
          public          postgres    false    232            �            1259    43637    sms_app_bodyinfo    TABLE     e   CREATE TABLE public.sms_app_bodyinfo (
    id bigint NOT NULL,
    bo_body character varying(100)
);
 $   DROP TABLE public.sms_app_bodyinfo;
       public         heap    postgres    false            �            1259    43636    sms_app_bodyinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_bodyinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.sms_app_bodyinfo_id_seq;
       public          postgres    false    235            k           0    0    sms_app_bodyinfo_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.sms_app_bodyinfo_id_seq OWNED BY public.sms_app_bodyinfo.id;
          public          postgres    false    234            k           1259    44885    sms_app_check_in_out    TABLE     |   CREATE TABLE public.sms_app_check_in_out (
    id bigint NOT NULL,
    check_in_out_name character varying(100) NOT NULL
);
 (   DROP TABLE public.sms_app_check_in_out;
       public         heap    postgres    false            j           1259    44884    sms_app_check_in_out_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_check_in_out_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_check_in_out_id_seq;
       public          postgres    false    363            l           0    0    sms_app_check_in_out_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_check_in_out_id_seq OWNED BY public.sms_app_check_in_out.id;
          public          postgres    false    362            �            1259    43644    sms_app_city    TABLE     �   CREATE TABLE public.sms_app_city (
    id bigint NOT NULL,
    city_name character varying(100) NOT NULL,
    country_id bigint NOT NULL,
    state_id bigint NOT NULL
);
     DROP TABLE public.sms_app_city;
       public         heap    postgres    false            �            1259    43643    sms_app_city_id_seq    SEQUENCE     |   CREATE SEQUENCE public.sms_app_city_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.sms_app_city_id_seq;
       public          postgres    false    237            m           0    0    sms_app_city_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.sms_app_city_id_seq OWNED BY public.sms_app_city.id;
          public          postgres    false    236            g           1259    44131    sms_app_consignmentdetailinfo    TABLE     �  CREATE TABLE public.sms_app_consignmentdetailinfo (
    id bigint NOT NULL,
    co_enquirynumber character varying(10) NOT NULL,
    co_consignmentnumber character varying(10) NOT NULL,
    co_consignmentdate character varying(10) NOT NULL,
    co_consigner character varying(10) NOT NULL,
    co_consignee character varying(10) NOT NULL,
    co_consignerinvoice character varying(30) NOT NULL,
    co_consignervalue integer NOT NULL,
    co_valueininr integer NOT NULL,
    co_noofpieces integer NOT NULL,
    co_weight integer NOT NULL,
    co_ebillno character varying(10) NOT NULL,
    co_dateofissue character varying(10) NOT NULL,
    co_dateofvalidity character varying(10) NOT NULL,
    co_containerdescription character varying(10) NOT NULL,
    co_dimension character varying(10) NOT NULL,
    co_lastmodifiedby character varying(30) NOT NULL,
    co_movement_id bigint NOT NULL,
    co_status_id bigint NOT NULL
);
 1   DROP TABLE public.sms_app_consignmentdetailinfo;
       public         heap    postgres    false            f           1259    44130 $   sms_app_consignmentdetailinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_consignmentdetailinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ;   DROP SEQUENCE public.sms_app_consignmentdetailinfo_id_seq;
       public          postgres    false    359            n           0    0 $   sms_app_consignmentdetailinfo_id_seq    SEQUENCE OWNED BY     m   ALTER SEQUENCE public.sms_app_consignmentdetailinfo_id_seq OWNED BY public.sms_app_consignmentdetailinfo.id;
          public          postgres    false    358            �            1259    43651    sms_app_country    TABLE     i   CREATE TABLE public.sms_app_country (
    id bigint NOT NULL,
    country_name character varying(100)
);
 #   DROP TABLE public.sms_app_country;
       public         heap    postgres    false            �            1259    43650    sms_app_country_id_seq    SEQUENCE        CREATE SEQUENCE public.sms_app_country_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.sms_app_country_id_seq;
       public          postgres    false    239            o           0    0    sms_app_country_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.sms_app_country_id_seq OWNED BY public.sms_app_country.id;
          public          postgres    false    238            �            1259    43658    sms_app_crcountfrominfo    TABLE     s   CREATE TABLE public.sms_app_crcountfrominfo (
    id bigint NOT NULL,
    cf_crcountfrom character varying(100)
);
 +   DROP TABLE public.sms_app_crcountfrominfo;
       public         heap    postgres    false            �            1259    43657    sms_app_crcountfrominfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_crcountfrominfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_crcountfrominfo_id_seq;
       public          postgres    false    241            p           0    0    sms_app_crcountfrominfo_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_crcountfrominfo_id_seq OWNED BY public.sms_app_crcountfrominfo.id;
          public          postgres    false    240            �            1259    43665    sms_app_currency_type    TABLE     �   CREATE TABLE public.sms_app_currency_type (
    id bigint NOT NULL,
    currency_type character varying(50),
    converision_value double precision
);
 )   DROP TABLE public.sms_app_currency_type;
       public         heap    postgres    false            �            1259    43664    sms_app_currency_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_currency_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.sms_app_currency_type_id_seq;
       public          postgres    false    243            q           0    0    sms_app_currency_type_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.sms_app_currency_type_id_seq OWNED BY public.sms_app_currency_type.id;
          public          postgres    false    242            �            1259    43672    sms_app_customerdepartmentinfo    TABLE     �   CREATE TABLE public.sms_app_customerdepartmentinfo (
    id bigint NOT NULL,
    ct_customerdepartment character varying(100)
);
 2   DROP TABLE public.sms_app_customerdepartmentinfo;
       public         heap    postgres    false            �            1259    43671 %   sms_app_customerdepartmentinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_customerdepartmentinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 <   DROP SEQUENCE public.sms_app_customerdepartmentinfo_id_seq;
       public          postgres    false    245            r           0    0 %   sms_app_customerdepartmentinfo_id_seq    SEQUENCE OWNED BY     o   ALTER SEQUENCE public.sms_app_customerdepartmentinfo_id_seq OWNED BY public.sms_app_customerdepartmentinfo.id;
          public          postgres    false    244            �            1259    43679    sms_app_customerinfo    TABLE     "  CREATE TABLE public.sms_app_customerinfo (
    id bigint NOT NULL,
    cu_customercode character varying(10) NOT NULL,
    cu_name character varying(10) NOT NULL,
    cu_nameshort character varying(10) NOT NULL,
    cu_pan character varying(10) NOT NULL,
    cu_gst character varying(10) NOT NULL,
    cu_customerperson character varying(30) NOT NULL,
    cu_designation character varying(10) NOT NULL,
    cu_contactno character varying(10) NOT NULL,
    cu_email character varying(50) NOT NULL,
    cu_gstpercentage character varying(10) NOT NULL,
    cu_creditdays character varying(10) NOT NULL,
    cu_paymentcycle character varying(30) NOT NULL,
    cu_tallyid character varying(30) NOT NULL,
    cu_lastmodifiedby character varying(30) NOT NULL,
    cu_businessmodel_id bigint NOT NULL,
    cu_creditcountfrom_id bigint NOT NULL,
    cu_department_id bigint NOT NULL,
    cu_gstexcepmtion_id bigint NOT NULL,
    cu_gstmodel_id bigint NOT NULL,
    cu_paymenttype_id bigint NOT NULL,
    cu_state_id bigint NOT NULL,
    cu_type_id bigint NOT NULL
);
 (   DROP TABLE public.sms_app_customerinfo;
       public         heap    postgres    false            �            1259    43678    sms_app_customerinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_customerinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_customerinfo_id_seq;
       public          postgres    false    247            s           0    0    sms_app_customerinfo_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_customerinfo_id_seq OWNED BY public.sms_app_customerinfo.id;
          public          postgres    false    246            �            1259    43686    sms_app_customernameinfo_new    TABLE     y   CREATE TABLE public.sms_app_customernameinfo_new (
    id bigint NOT NULL,
    cn_customername character varying(100)
);
 0   DROP TABLE public.sms_app_customernameinfo_new;
       public         heap    postgres    false            �            1259    43685 #   sms_app_customernameinfo_new_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_customernameinfo_new_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 :   DROP SEQUENCE public.sms_app_customernameinfo_new_id_seq;
       public          postgres    false    249            t           0    0 #   sms_app_customernameinfo_new_id_seq    SEQUENCE OWNED BY     k   ALTER SEQUENCE public.sms_app_customernameinfo_new_id_seq OWNED BY public.sms_app_customernameinfo_new.id;
          public          postgres    false    248            �            1259    43693    sms_app_customertypeinfo    TABLE     x   CREATE TABLE public.sms_app_customertypeinfo (
    id bigint NOT NULL,
    cust_customer_type character varying(100)
);
 ,   DROP TABLE public.sms_app_customertypeinfo;
       public         heap    postgres    false            �            1259    43692    sms_app_customertypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_customertypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.sms_app_customertypeinfo_id_seq;
       public          postgres    false    251            u           0    0    sms_app_customertypeinfo_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.sms_app_customertypeinfo_id_seq OWNED BY public.sms_app_customertypeinfo.id;
          public          postgres    false    250            �            1259    43700    sms_app_damageinfo    TABLE     j   CREATE TABLE public.sms_app_damageinfo (
    id bigint NOT NULL,
    damage_name character varying(20)
);
 &   DROP TABLE public.sms_app_damageinfo;
       public         heap    postgres    false            �            1259    43699    sms_app_damageinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_damageinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.sms_app_damageinfo_id_seq;
       public          postgres    false    253            v           0    0    sms_app_damageinfo_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.sms_app_damageinfo_id_seq OWNED BY public.sms_app_damageinfo.id;
          public          postgres    false    252            s           1259    45108    sms_app_damagereportimages    TABLE     �  CREATE TABLE public.sms_app_damagereportimages (
    id bigint NOT NULL,
    "dam_OTL_pic" character varying(100),
    damimage_wh_job_num character varying(300),
    dam_document character varying(100),
    dam_50_offload_pic character varying(100),
    dam_closed_door_pic character varying(100),
    dam_empty_vehicle character varying(100),
    dam_open_door_pic character varying(100)
);
 .   DROP TABLE public.sms_app_damagereportimages;
       public         heap    postgres    false            r           1259    45107 !   sms_app_damagereportimages_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_damagereportimages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.sms_app_damagereportimages_id_seq;
       public          postgres    false    371            w           0    0 !   sms_app_damagereportimages_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.sms_app_damagereportimages_id_seq OWNED BY public.sms_app_damagereportimages.id;
          public          postgres    false    370            e           1259    44089    sms_app_damagereportinfo    TABLE     �   CREATE TABLE public.sms_app_damagereportinfo (
    id bigint NOT NULL,
    dam_wh_job_num character varying(300),
    "dam_GRN_num" character varying(300),
    dam_damage_type_id bigint,
    dam_status_id bigint
);
 ,   DROP TABLE public.sms_app_damagereportinfo;
       public         heap    postgres    false            d           1259    44088    sms_app_damagereportinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_damagereportinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.sms_app_damagereportinfo_id_seq;
       public          postgres    false    357            x           0    0    sms_app_damagereportinfo_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.sms_app_damagereportinfo_id_seq OWNED BY public.sms_app_damagereportinfo.id;
          public          postgres    false    356            �            1259    43707    sms_app_department_info    TABLE     �   CREATE TABLE public.sms_app_department_info (
    id bigint NOT NULL,
    dept_name character varying(100) NOT NULL,
    dept_status_id bigint NOT NULL
);
 +   DROP TABLE public.sms_app_department_info;
       public         heap    postgres    false            �            1259    43706    sms_app_department_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_department_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_department_info_id_seq;
       public          postgres    false    255            y           0    0    sms_app_department_info_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_department_info_id_seq OWNED BY public.sms_app_department_info.id;
          public          postgres    false    254                       1259    43714    sms_app_designationinfo    TABLE     y   CREATE TABLE public.sms_app_designationinfo (
    id bigint NOT NULL,
    des_designation_name character varying(100)
);
 +   DROP TABLE public.sms_app_designationinfo;
       public         heap    postgres    false                        1259    43713    sms_app_designationinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_designationinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_designationinfo_id_seq;
       public          postgres    false    257            z           0    0    sms_app_designationinfo_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_designationinfo_id_seq OWNED BY public.sms_app_designationinfo.id;
          public          postgres    false    256            y           1259    45204    sms_app_dispatch_info    TABLE       CREATE TABLE public.sms_app_dispatch_info (
    id bigint NOT NULL,
    dispatch_depature_date character varying(20),
    dispatch_driver character varying(20),
    dispatch_contact_number character varying(20),
    "dispatch_DL_number" character varying(20),
    dispatch_otl character varying(20),
    dispatch_transporter character varying(100),
    dispatch_truck_number character varying(20),
    "dispatch_HAWB" character varying(20),
    "dispatch_MAWB" character varying(20),
    dispatch_destination character varying(20),
    dispatch_comments character varying(20),
    dispatch_cargo_picked bigint,
    dispatch_status_id bigint,
    "dispatch_sticker_pasted_BVM" bigint,
    dispatch_truck_type_id bigint NOT NULL,
    dispatch_num character varying(20)
);
 )   DROP TABLE public.sms_app_dispatch_info;
       public         heap    postgres    false            x           1259    45203    sms_app_dispatch_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_dispatch_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.sms_app_dispatch_info_id_seq;
       public          postgres    false    377            {           0    0    sms_app_dispatch_info_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.sms_app_dispatch_info_id_seq OWNED BY public.sms_app_dispatch_info.id;
          public          postgres    false    376            c           1259    44075    sms_app_employee    TABLE       CREATE TABLE public.sms_app_employee (
    id bigint NOT NULL,
    emp_empid character varying(100) NOT NULL,
    emp_full_name character varying(100) NOT NULL,
    emp_email character varying(50) NOT NULL,
    emp_contact character varying(10) NOT NULL,
    emp_designation character varying(10) NOT NULL,
    emp_branch character varying(10) NOT NULL,
    emp_password character varying(100) NOT NULL,
    emp_password_conf character varying(100) NOT NULL,
    emp_role character varying(10) NOT NULL,
    emp_status_id bigint NOT NULL
);
 $   DROP TABLE public.sms_app_employee;
       public         heap    postgres    false            b           1259    44074    sms_app_employee_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_employee_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.sms_app_employee_id_seq;
       public          postgres    false    355            |           0    0    sms_app_employee_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.sms_app_employee_id_seq OWNED BY public.sms_app_employee.id;
          public          postgres    false    354                       1259    43721    sms_app_enquiry_info    TABLE     �   CREATE TABLE public.sms_app_enquiry_info (
    id bigint NOT NULL,
    enq_enquiry_number character varying(10) NOT NULL,
    enq_customer_name character varying(10) NOT NULL
);
 (   DROP TABLE public.sms_app_enquiry_info;
       public         heap    postgres    false                       1259    43720    sms_app_enquiry_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_enquiry_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_enquiry_info_id_seq;
       public          postgres    false    259            }           0    0    sms_app_enquiry_info_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_enquiry_info_id_seq OWNED BY public.sms_app_enquiry_info.id;
          public          postgres    false    258            a           1259    44068    sms_app_enquirynoteinfo    TABLE        CREATE TABLE public.sms_app_enquirynoteinfo (
    id bigint NOT NULL,
    en_enquirynumber character varying(10) NOT NULL,
    en_othercustomer character varying(10) NOT NULL,
    en_customercode character varying(10) NOT NULL,
    en_customercontact character varying(30) NOT NULL,
    en_customeremail character varying(30) NOT NULL,
    en_raisedon character varying(30) NOT NULL,
    en_raisedby character varying(30) NOT NULL,
    en_lastmodifiedby character varying(30) NOT NULL,
    en_assignedto_id integer NOT NULL,
    en_customerdepartment_id bigint NOT NULL,
    en_customername_id bigint NOT NULL,
    en_fromlocaion bigint NOT NULL,
    en_status_id bigint NOT NULL,
    en_tolocation bigint NOT NULL,
    en_vehiclecategory_id bigint NOT NULL,
    en_vehicletype_id bigint NOT NULL
);
 +   DROP TABLE public.sms_app_enquirynoteinfo;
       public         heap    postgres    false            `           1259    44067    sms_app_enquirynoteinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_enquirynoteinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_enquirynoteinfo_id_seq;
       public          postgres    false    353            ~           0    0    sms_app_enquirynoteinfo_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_enquirynoteinfo_id_seq OWNED BY public.sms_app_enquirynoteinfo.id;
          public          postgres    false    352                       1259    43728    sms_app_fueltypeinfo    TABLE     m   CREATE TABLE public.sms_app_fueltypeinfo (
    id bigint NOT NULL,
    ft_fueltype character varying(100)
);
 (   DROP TABLE public.sms_app_fueltypeinfo;
       public         heap    postgres    false                       1259    43727    sms_app_fueltypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_fueltypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_fueltypeinfo_id_seq;
       public          postgres    false    261                       0    0    sms_app_fueltypeinfo_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_fueltypeinfo_id_seq OWNED BY public.sms_app_fueltypeinfo.id;
          public          postgres    false    260            _           1259    44061    sms_app_gatein_info    TABLE     �  CREATE TABLE public.sms_app_gatein_info (
    id bigint NOT NULL,
    gatein_job_no character varying(20) NOT NULL,
    gatein_invoice character varying(20) NOT NULL,
    gatein_customer_type_id bigint NOT NULL,
    gatein_arrival_date character varying(20),
    gatein_shipper character varying(20),
    gatein_consignee character varying(20),
    gatein_no_of_pkg integer,
    gatein_weight integer,
    gatein_driver character varying(20),
    gatein_contact_number character varying(20),
    "gatein_DL_number" character varying(20),
    gatein_otl character varying(20),
    gatein_transporter character varying(100),
    gatein_truck_number character varying(20),
    gatein_customer_id bigint NOT NULL,
    gatein_status_id bigint,
    gatein_truck_type_id bigint NOT NULL,
    gatein_department_id bigint NOT NULL,
    gatein_created_at timestamp with time zone,
    gatein_updated_at timestamp with time zone
);
 '   DROP TABLE public.sms_app_gatein_info;
       public         heap    postgres    false            ^           1259    44060    sms_app_gatein_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_gatein_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.sms_app_gatein_info_id_seq;
       public          postgres    false    351            �           0    0    sms_app_gatein_info_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.sms_app_gatein_info_id_seq OWNED BY public.sms_app_gatein_info.id;
          public          postgres    false    350                       1259    43735    sms_app_gstexcemptioninfo    TABLE     w   CREATE TABLE public.sms_app_gstexcemptioninfo (
    id bigint NOT NULL,
    ge_gstexcepmtion character varying(100)
);
 -   DROP TABLE public.sms_app_gstexcemptioninfo;
       public         heap    postgres    false                       1259    43734     sms_app_gstexcemptioninfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_gstexcemptioninfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_gstexcemptioninfo_id_seq;
       public          postgres    false    263            �           0    0     sms_app_gstexcemptioninfo_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_gstexcemptioninfo_id_seq OWNED BY public.sms_app_gstexcemptioninfo.id;
          public          postgres    false    262            	           1259    43742    sms_app_gstmodelinfo    TABLE     m   CREATE TABLE public.sms_app_gstmodelinfo (
    id bigint NOT NULL,
    gm_gstmodel character varying(100)
);
 (   DROP TABLE public.sms_app_gstmodelinfo;
       public         heap    postgres    false                       1259    43741    sms_app_gstmodelinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_gstmodelinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_gstmodelinfo_id_seq;
       public          postgres    false    265            �           0    0    sms_app_gstmodelinfo_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_gstmodelinfo_id_seq OWNED BY public.sms_app_gstmodelinfo.id;
          public          postgres    false    264            ]           1259    44054    sms_app_insurance_info    TABLE     p  CREATE TABLE public.sms_app_insurance_info (
    id bigint NOT NULL,
    ins_name character varying(40) NOT NULL,
    ins_start_date character varying(10) NOT NULL,
    ins_expiry_date character varying(10) NOT NULL,
    ins_units character varying(10) NOT NULL,
    ins_status_id bigint NOT NULL,
    ins_type_id bigint NOT NULL,
    ins_vendor_id bigint NOT NULL
);
 *   DROP TABLE public.sms_app_insurance_info;
       public         heap    postgres    false            \           1259    44053    sms_app_insurance_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_insurance_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.sms_app_insurance_info_id_seq;
       public          postgres    false    349            �           0    0    sms_app_insurance_info_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.sms_app_insurance_info_id_seq OWNED BY public.sms_app_insurance_info.id;
          public          postgres    false    348                       1259    43749    sms_app_insurance_type    TABLE     q   CREATE TABLE public.sms_app_insurance_type (
    id bigint NOT NULL,
    insurance_name character varying(50)
);
 *   DROP TABLE public.sms_app_insurance_type;
       public         heap    postgres    false            
           1259    43748    sms_app_insurance_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_insurance_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.sms_app_insurance_type_id_seq;
       public          postgres    false    267            �           0    0    sms_app_insurance_type_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.sms_app_insurance_type_id_seq OWNED BY public.sms_app_insurance_type.id;
          public          postgres    false    266            [           1259    44047    sms_app_loadingbay_info    TABLE     k  CREATE TABLE public.sms_app_loadingbay_info (
    id bigint NOT NULL,
    lb_job_no character varying(20) NOT NULL,
    lb_invoice character varying(20) NOT NULL,
    lb_eway_bill character varying(20) NOT NULL,
    lb_validity_date character varying(20) NOT NULL,
    lb_stock_unloading_start_time character varying(20),
    lb_stock_unloading_end_time character varying(20),
    "lb_stock_FRD_time" character varying(20),
    lb_stock_invoice_value double precision,
    lb_stock_amount_in double precision,
    lb_offload_acceptance bigint NOT NULL,
    lb_otl_check bigint NOT NULL,
    lb_packing_list bigint NOT NULL,
    lb_status_id bigint,
    lb_stock_invoice_currency_id bigint,
    lb_stock_type_id bigint,
    lb_stock_currency_con double precision,
    lb_mh_crane boolean,
    lb_mh_forklift boolean,
    lb_mh_handtrolley boolean,
    lb_mh_manual boolean
);
 +   DROP TABLE public.sms_app_loadingbay_info;
       public         heap    postgres    false            Z           1259    44046    sms_app_loadingbay_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_loadingbay_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_loadingbay_info_id_seq;
       public          postgres    false    347            �           0    0    sms_app_loadingbay_info_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_loadingbay_info_id_seq OWNED BY public.sms_app_loadingbay_info.id;
          public          postgres    false    346            {           1259    45300    sms_app_loadingbayimages_info    TABLE     �   CREATE TABLE public.sms_app_loadingbayimages_info (
    id bigint NOT NULL,
    lbimg_job_no character varying(300),
    lbimg_inward_pod character varying(100)
);
 1   DROP TABLE public.sms_app_loadingbayimages_info;
       public         heap    postgres    false            z           1259    45299 $   sms_app_loadingbayimages_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_loadingbayimages_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ;   DROP SEQUENCE public.sms_app_loadingbayimages_info_id_seq;
       public          postgres    false    379            �           0    0 $   sms_app_loadingbayimages_info_id_seq    SEQUENCE OWNED BY     m   ALTER SEQUENCE public.sms_app_loadingbayimages_info_id_seq OWNED BY public.sms_app_loadingbayimages_info.id;
          public          postgres    false    378                       1259    43756    sms_app_location_info    TABLE     _  CREATE TABLE public.sms_app_location_info (
    id bigint NOT NULL,
    loc_name character varying(100) NOT NULL,
    loc_zipcode character varying(10) NOT NULL,
    loc_address character varying(300) NOT NULL,
    loc_city_id bigint NOT NULL,
    loc_country_id bigint NOT NULL,
    loc_state_id bigint NOT NULL,
    loc_status_id bigint NOT NULL
);
 )   DROP TABLE public.sms_app_location_info;
       public         heap    postgres    false                       1259    43755    sms_app_location_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_location_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.sms_app_location_info_id_seq;
       public          postgres    false    269            �           0    0    sms_app_location_info_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.sms_app_location_info_id_seq OWNED BY public.sms_app_location_info.id;
          public          postgres    false    268            Y           1259    44030    sms_app_locationmasterinfo    TABLE     �  CREATE TABLE public.sms_app_locationmasterinfo (
    id bigint NOT NULL,
    lm_length double precision NOT NULL,
    lm_width double precision NOT NULL,
    lm_height double precision NOT NULL,
    lm_size double precision NOT NULL,
    lm_area_occupied double precision NOT NULL,
    lm_available_area double precision NOT NULL,
    lm_total_volume double precision NOT NULL,
    lm_available_volume double precision NOT NULL,
    lm_volume_occupied double precision NOT NULL,
    lm_concatenate character varying(10) NOT NULL,
    lm_customer_model_id bigint NOT NULL,
    lm_areaside_id bigint NOT NULL,
    lm_customer_name_id bigint NOT NULL,
    lm_wh_location_id bigint NOT NULL,
    lm_wh_unit_id bigint NOT NULL
);
 .   DROP TABLE public.sms_app_locationmasterinfo;
       public         heap    postgres    false            X           1259    44029 !   sms_app_locationmasterinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_locationmasterinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.sms_app_locationmasterinfo_id_seq;
       public          postgres    false    345            �           0    0 !   sms_app_locationmasterinfo_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.sms_app_locationmasterinfo_id_seq OWNED BY public.sms_app_locationmasterinfo.id;
          public          postgres    false    344                       1259    43763    sms_app_materialhandling_info    TABLE     s   CREATE TABLE public.sms_app_materialhandling_info (
    id bigint NOT NULL,
    "MH_name" character varying(20)
);
 1   DROP TABLE public.sms_app_materialhandling_info;
       public         heap    postgres    false                       1259    43762 $   sms_app_materialhandling_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_materialhandling_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ;   DROP SEQUENCE public.sms_app_materialhandling_info_id_seq;
       public          postgres    false    271            �           0    0 $   sms_app_materialhandling_info_id_seq    SEQUENCE OWNED BY     m   ALTER SEQUENCE public.sms_app_materialhandling_info_id_seq OWNED BY public.sms_app_materialhandling_info.id;
          public          postgres    false    270                       1259    43770    sms_app_movementtypeinfo    TABLE     u   CREATE TABLE public.sms_app_movementtypeinfo (
    id bigint NOT NULL,
    mt_movementtype character varying(100)
);
 ,   DROP TABLE public.sms_app_movementtypeinfo;
       public         heap    postgres    false                       1259    43769    sms_app_movementtypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_movementtypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.sms_app_movementtypeinfo_id_seq;
       public          postgres    false    273            �           0    0    sms_app_movementtypeinfo_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.sms_app_movementtypeinfo_id_seq OWNED BY public.sms_app_movementtypeinfo.id;
          public          postgres    false    272                       1259    43777    sms_app_ownershipinfo    TABLE     o   CREATE TABLE public.sms_app_ownershipinfo (
    id bigint NOT NULL,
    ow_ownership character varying(100)
);
 )   DROP TABLE public.sms_app_ownershipinfo;
       public         heap    postgres    false                       1259    43776    sms_app_ownershipinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_ownershipinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.sms_app_ownershipinfo_id_seq;
       public          postgres    false    275            �           0    0    sms_app_ownershipinfo_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.sms_app_ownershipinfo_id_seq OWNED BY public.sms_app_ownershipinfo.id;
          public          postgres    false    274                       1259    43784    sms_app_packagetype_info    TABLE     q   CREATE TABLE public.sms_app_packagetype_info (
    id bigint NOT NULL,
    package_type character varying(50)
);
 ,   DROP TABLE public.sms_app_packagetype_info;
       public         heap    postgres    false                       1259    43783    sms_app_packagetype_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_packagetype_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.sms_app_packagetype_info_id_seq;
       public          postgres    false    277            �           0    0    sms_app_packagetype_info_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.sms_app_packagetype_info_id_seq OWNED BY public.sms_app_packagetype_info.id;
          public          postgres    false    276                       1259    43791    sms_app_paymenttypeinfo    TABLE     s   CREATE TABLE public.sms_app_paymenttypeinfo (
    id bigint NOT NULL,
    pa_paymenttype character varying(100)
);
 +   DROP TABLE public.sms_app_paymenttypeinfo;
       public         heap    postgres    false                       1259    43790    sms_app_paymenttypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_paymenttypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_paymenttypeinfo_id_seq;
       public          postgres    false    279            �           0    0    sms_app_paymenttypeinfo_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_paymenttypeinfo_id_seq OWNED BY public.sms_app_paymenttypeinfo.id;
          public          postgres    false    278                       1259    43798    sms_app_peo_reg    TABLE     �   CREATE TABLE public.sms_app_peo_reg (
    id bigint NOT NULL,
    peo_name character varying(100) NOT NULL,
    peo_age integer NOT NULL,
    peo_mob integer NOT NULL,
    peo_address character varying(100) NOT NULL
);
 #   DROP TABLE public.sms_app_peo_reg;
       public         heap    postgres    false                       1259    43797    sms_app_peo_reg_id_seq    SEQUENCE        CREATE SEQUENCE public.sms_app_peo_reg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.sms_app_peo_reg_id_seq;
       public          postgres    false    281            �           0    0    sms_app_peo_reg_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.sms_app_peo_reg_id_seq OWNED BY public.sms_app_peo_reg.id;
          public          postgres    false    280                       1259    43805    sms_app_permittypeinfo    TABLE     q   CREATE TABLE public.sms_app_permittypeinfo (
    id bigint NOT NULL,
    pt_permittype character varying(100)
);
 *   DROP TABLE public.sms_app_permittypeinfo;
       public         heap    postgres    false                       1259    43804    sms_app_permittypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_permittypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.sms_app_permittypeinfo_id_seq;
       public          postgres    false    283            �           0    0    sms_app_permittypeinfo_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.sms_app_permittypeinfo_id_seq OWNED BY public.sms_app_permittypeinfo.id;
          public          postgres    false    282                       1259    43812    sms_app_prod_cat    TABLE     l   CREATE TABLE public.sms_app_prod_cat (
    id bigint NOT NULL,
    prod_cat_title character varying(100)
);
 $   DROP TABLE public.sms_app_prod_cat;
       public         heap    postgres    false                       1259    43811    sms_app_prod_cat_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_prod_cat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.sms_app_prod_cat_id_seq;
       public          postgres    false    285            �           0    0    sms_app_prod_cat_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.sms_app_prod_cat_id_seq OWNED BY public.sms_app_prod_cat.id;
          public          postgres    false    284                       1259    43819    sms_app_prod_type    TABLE     n   CREATE TABLE public.sms_app_prod_type (
    id bigint NOT NULL,
    prod_type_title character varying(100)
);
 %   DROP TABLE public.sms_app_prod_type;
       public         heap    postgres    false                       1259    43818    sms_app_prod_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_prod_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.sms_app_prod_type_id_seq;
       public          postgres    false    287            �           0    0    sms_app_prod_type_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.sms_app_prod_type_id_seq OWNED BY public.sms_app_prod_type.id;
          public          postgres    false    286            W           1259    44023    sms_app_product_info    TABLE     �   CREATE TABLE public.sms_app_product_info (
    id bigint NOT NULL,
    prod_name character varying(100) NOT NULL,
    prod_description character varying(50) NOT NULL,
    prod_type_id bigint NOT NULL
);
 (   DROP TABLE public.sms_app_product_info;
       public         heap    postgres    false            V           1259    44022    sms_app_product_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_product_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_product_info_id_seq;
       public          postgres    false    343            �           0    0    sms_app_product_info_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_product_info_id_seq OWNED BY public.sms_app_product_info.id;
          public          postgres    false    342            o           1259    45045    sms_app_received_not    TABLE     |   CREATE TABLE public.sms_app_received_not (
    id bigint NOT NULL,
    received_not_name character varying(100) NOT NULL
);
 (   DROP TABLE public.sms_app_received_not;
       public         heap    postgres    false            n           1259    45044    sms_app_received_not_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_received_not_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_received_not_id_seq;
       public          postgres    false    367            �           0    0    sms_app_received_not_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_received_not_id_seq OWNED BY public.sms_app_received_not.id;
          public          postgres    false    366            !           1259    43826    sms_app_roleinfo    TABLE     g   CREATE TABLE public.sms_app_roleinfo (
    id bigint NOT NULL,
    role_name character varying(100)
);
 $   DROP TABLE public.sms_app_roleinfo;
       public         heap    postgres    false                        1259    43825    sms_app_roleinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_roleinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.sms_app_roleinfo_id_seq;
       public          postgres    false    289            �           0    0    sms_app_roleinfo_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.sms_app_roleinfo_id_seq OWNED BY public.sms_app_roleinfo.id;
          public          postgres    false    288            U           1259    44016    sms_app_rtratemasterinfo    TABLE     %  CREATE TABLE public.sms_app_rtratemasterinfo (
    id bigint NOT NULL,
    ro_rate integer NOT NULL,
    ro_customer_id bigint NOT NULL,
    ro_customerdepartment_id bigint NOT NULL,
    ro_fromlocation bigint NOT NULL,
    ro_tolocation bigint NOT NULL,
    ro_vehicletype bigint NOT NULL
);
 ,   DROP TABLE public.sms_app_rtratemasterinfo;
       public         heap    postgres    false            T           1259    44015    sms_app_rtratemasterinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_rtratemasterinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.sms_app_rtratemasterinfo_id_seq;
       public          postgres    false    341            �           0    0    sms_app_rtratemasterinfo_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.sms_app_rtratemasterinfo_id_seq OWNED BY public.sms_app_rtratemasterinfo.id;
          public          postgres    false    340            S           1259    44009    sms_app_service_info    TABLE     6  CREATE TABLE public.sms_app_service_info (
    id bigint NOT NULL,
    ser_start_date character varying(10) NOT NULL,
    ser_end_date character varying(10) NOT NULL,
    ser_cost numeric(10,2) NOT NULL,
    ser_asset_id bigint NOT NULL,
    ser_status_id bigint NOT NULL,
    ser_vendor_id bigint NOT NULL
);
 (   DROP TABLE public.sms_app_service_info;
       public         heap    postgres    false            R           1259    44008    sms_app_service_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_service_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_service_info_id_seq;
       public          postgres    false    339            �           0    0    sms_app_service_info_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_service_info_id_seq OWNED BY public.sms_app_service_info.id;
          public          postgres    false    338            w           1259    45191    sms_app_stackinginfo    TABLE     v   CREATE TABLE public.sms_app_stackinginfo (
    id bigint NOT NULL,
    stack_layer character varying(100) NOT NULL
);
 (   DROP TABLE public.sms_app_stackinginfo;
       public         heap    postgres    false            v           1259    45190    sms_app_stackinginfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_stackinginfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_stackinginfo_id_seq;
       public          postgres    false    375            �           0    0    sms_app_stackinginfo_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_stackinginfo_id_seq OWNED BY public.sms_app_stackinginfo.id;
          public          postgres    false    374            #           1259    43833    sms_app_state    TABLE     �   CREATE TABLE public.sms_app_state (
    id bigint NOT NULL,
    state_name character varying(100),
    country_id bigint NOT NULL
);
 !   DROP TABLE public.sms_app_state;
       public         heap    postgres    false            "           1259    43832    sms_app_state_id_seq    SEQUENCE     }   CREATE SEQUENCE public.sms_app_state_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.sms_app_state_id_seq;
       public          postgres    false    291            �           0    0    sms_app_state_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.sms_app_state_id_seq OWNED BY public.sms_app_state.id;
          public          postgres    false    290            %           1259    43840    sms_app_statuslist    TABLE     l   CREATE TABLE public.sms_app_statuslist (
    id bigint NOT NULL,
    status_title character varying(100)
);
 &   DROP TABLE public.sms_app_statuslist;
       public         heap    postgres    false            $           1259    43839    sms_app_statuslist_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_statuslist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.sms_app_statuslist_id_seq;
       public          postgres    false    293            �           0    0    sms_app_statuslist_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.sms_app_statuslist_id_seq OWNED BY public.sms_app_statuslist.id;
          public          postgres    false    292            '           1259    43847    sms_app_stock_movement_type    TABLE     v   CREATE TABLE public.sms_app_stock_movement_type (
    id bigint NOT NULL,
    stock_mov_type character varying(50)
);
 /   DROP TABLE public.sms_app_stock_movement_type;
       public         heap    postgres    false            &           1259    43846 "   sms_app_stock_movement_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_stock_movement_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.sms_app_stock_movement_type_id_seq;
       public          postgres    false    295            �           0    0 "   sms_app_stock_movement_type_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.sms_app_stock_movement_type_id_seq OWNED BY public.sms_app_stock_movement_type.id;
          public          postgres    false    294            )           1259    43854    sms_app_stock_type    TABLE     i   CREATE TABLE public.sms_app_stock_type (
    id bigint NOT NULL,
    stock_type character varying(50)
);
 &   DROP TABLE public.sms_app_stock_type;
       public         heap    postgres    false            (           1259    43853    sms_app_stock_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_stock_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.sms_app_stock_type_id_seq;
       public          postgres    false    297            �           0    0    sms_app_stock_type_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.sms_app_stock_type_id_seq OWNED BY public.sms_app_stock_type.id;
          public          postgres    false    296            +           1259    43861    sms_app_stud_reg    TABLE     4  CREATE TABLE public.sms_app_stud_reg (
    id bigint NOT NULL,
    stud_name character varying(100) NOT NULL,
    stud_age integer NOT NULL,
    stud_eng integer NOT NULL,
    stud_tamil integer NOT NULL,
    stud_math integer NOT NULL,
    stud_social integer NOT NULL,
    stud_science integer NOT NULL
);
 $   DROP TABLE public.sms_app_stud_reg;
       public         heap    postgres    false            *           1259    43860    sms_app_stud_reg_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_stud_reg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.sms_app_stud_reg_id_seq;
       public          postgres    false    299            �           0    0    sms_app_stud_reg_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.sms_app_stud_reg_id_seq OWNED BY public.sms_app_stud_reg.id;
          public          postgres    false    298            -           1259    43868    sms_app_trbusinesstypeinfo    TABLE     y   CREATE TABLE public.sms_app_trbusinesstypeinfo (
    id bigint NOT NULL,
    tb_trbusinesstype character varying(100)
);
 .   DROP TABLE public.sms_app_trbusinesstypeinfo;
       public         heap    postgres    false            ,           1259    43867 !   sms_app_trbusinesstypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_trbusinesstypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.sms_app_trbusinesstypeinfo_id_seq;
       public          postgres    false    301            �           0    0 !   sms_app_trbusinesstypeinfo_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.sms_app_trbusinesstypeinfo_id_seq OWNED BY public.sms_app_trbusinesstypeinfo.id;
          public          postgres    false    300            Q           1259    44002    sms_app_tripclosureinfo    TABLE     �  CREATE TABLE public.sms_app_tripclosureinfo (
    id bigint NOT NULL,
    tc_enquirynumber character varying(10) NOT NULL,
    tc_consignmentnumber character varying(10) NOT NULL,
    tc_tripcost integer NOT NULL,
    tc_parkingcost integer NOT NULL,
    tc_tollcost integer NOT NULL,
    tc_loadingcost integer NOT NULL,
    tc_unloadingcost integer NOT NULL,
    tc_lastmodifiedby character varying(30) NOT NULL,
    tc_financestatus_id bigint NOT NULL
);
 +   DROP TABLE public.sms_app_tripclosureinfo;
       public         heap    postgres    false            P           1259    44001    sms_app_tripclosureinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_tripclosureinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_tripclosureinfo_id_seq;
       public          postgres    false    337            �           0    0    sms_app_tripclosureinfo_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_tripclosureinfo_id_seq OWNED BY public.sms_app_tripclosureinfo.id;
          public          postgres    false    336            O           1259    43995    sms_app_tripdetailinfo    TABLE     R  CREATE TABLE public.sms_app_tripdetailinfo (
    id bigint NOT NULL,
    tr_enquirynumber character varying(10) NOT NULL,
    tr_consignmentnumber character varying(10) NOT NULL,
    tr_tripnumber character varying(10) NOT NULL,
    tr_startingkm integer NOT NULL,
    tr_startingdate character varying(30) NOT NULL,
    tr_deliveryimages character varying(30) NOT NULL,
    tr_proofofdelivery character varying(30) NOT NULL,
    tr_sealnumber integer NOT NULL,
    tr_containernumber integer NOT NULL,
    tr_endingkm character varying(10) NOT NULL,
    tr_endingdate character varying(10) NOT NULL,
    tr_shipmentdetails character varying(10) NOT NULL,
    tr_lastmodifiedby character varying(30) NOT NULL,
    tr_fromlocation bigint NOT NULL,
    tr_status bigint NOT NULL,
    tr_tolocation bigint NOT NULL,
    tr_tripstatus bigint NOT NULL
);
 *   DROP TABLE public.sms_app_tripdetailinfo;
       public         heap    postgres    false            N           1259    43994    sms_app_tripdetailinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_tripdetailinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.sms_app_tripdetailinfo_id_seq;
       public          postgres    false    335            �           0    0    sms_app_tripdetailinfo_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.sms_app_tripdetailinfo_id_seq OWNED BY public.sms_app_tripdetailinfo.id;
          public          postgres    false    334            /           1259    43875    sms_app_unitinfo    TABLE     �   CREATE TABLE public.sms_app_unitinfo (
    id bigint NOT NULL,
    unit_name character varying(100) NOT NULL,
    ui_branch_name_id bigint NOT NULL
);
 $   DROP TABLE public.sms_app_unitinfo;
       public         heap    postgres    false            .           1259    43874    sms_app_unitinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_unitinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.sms_app_unitinfo_id_seq;
       public          postgres    false    303            �           0    0    sms_app_unitinfo_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.sms_app_unitinfo_id_seq OWNED BY public.sms_app_unitinfo.id;
          public          postgres    false    302            m           1259    44909    sms_app_uom    TABLE     j   CREATE TABLE public.sms_app_uom (
    id bigint NOT NULL,
    uom_name character varying(100) NOT NULL
);
    DROP TABLE public.sms_app_uom;
       public         heap    postgres    false            l           1259    44908    sms_app_uom_id_seq    SEQUENCE     {   CREATE SEQUENCE public.sms_app_uom_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.sms_app_uom_id_seq;
       public          postgres    false    365            �           0    0    sms_app_uom_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.sms_app_uom_id_seq OWNED BY public.sms_app_uom.id;
          public          postgres    false    364            q           1259    45062    sms_app_uploadinfo    TABLE     �   CREATE TABLE public.sms_app_uploadinfo (
    id bigint NOT NULL,
    file_upload_nam character varying(100) NOT NULL,
    image_upload_nam character varying(100) NOT NULL,
    upload_description character varying(100)
);
 &   DROP TABLE public.sms_app_uploadinfo;
       public         heap    postgres    false            p           1259    45061    sms_app_uploadinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_uploadinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.sms_app_uploadinfo_id_seq;
       public          postgres    false    369            �           0    0    sms_app_uploadinfo_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.sms_app_uploadinfo_id_seq OWNED BY public.sms_app_uploadinfo.id;
          public          postgres    false    368            M           1259    43986    sms_app_user_extinfo    TABLE     �  CREATE TABLE public.sms_app_user_extinfo (
    id bigint NOT NULL,
    emp_contact character varying(10),
    emp_pan character varying(10),
    emp_uan character varying(10),
    emp_esi character varying(10),
    emp_aadhar character varying(10),
    "emp_DOB" character varying(10),
    "emp_DOJ" character varying(10),
    department_id bigint,
    emp_branch_id bigint,
    emp_designation_id bigint,
    emp_role_id bigint,
    user_id integer
);
 (   DROP TABLE public.sms_app_user_extinfo;
       public         heap    postgres    false            L           1259    43985    sms_app_user_extinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_user_extinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.sms_app_user_extinfo_id_seq;
       public          postgres    false    333            �           0    0    sms_app_user_extinfo_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.sms_app_user_extinfo_id_seq OWNED BY public.sms_app_user_extinfo.id;
          public          postgres    false    332            1           1259    43882    sms_app_vehiclecategoryinfo    TABLE     {   CREATE TABLE public.sms_app_vehiclecategoryinfo (
    id bigint NOT NULL,
    vc_vehiclecategory character varying(100)
);
 /   DROP TABLE public.sms_app_vehiclecategoryinfo;
       public         heap    postgres    false            0           1259    43881 "   sms_app_vehiclecategoryinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehiclecategoryinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.sms_app_vehiclecategoryinfo_id_seq;
       public          postgres    false    305            �           0    0 "   sms_app_vehiclecategoryinfo_id_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.sms_app_vehiclecategoryinfo_id_seq OWNED BY public.sms_app_vehiclecategoryinfo.id;
          public          postgres    false    304            3           1259    43889    sms_app_vehiclecolourinfo    TABLE     w   CREATE TABLE public.sms_app_vehiclecolourinfo (
    id bigint NOT NULL,
    vh_vehiclecolour character varying(100)
);
 -   DROP TABLE public.sms_app_vehiclecolourinfo;
       public         heap    postgres    false            2           1259    43888     sms_app_vehiclecolourinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehiclecolourinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_vehiclecolourinfo_id_seq;
       public          postgres    false    307            �           0    0     sms_app_vehiclecolourinfo_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_vehiclecolourinfo_id_seq OWNED BY public.sms_app_vehiclecolourinfo.id;
          public          postgres    false    306            K           1259    43979    sms_app_vehicledetailinfo    TABLE        CREATE TABLE public.sms_app_vehicledetailinfo (
    id bigint NOT NULL,
    ve_enquirynumber character varying(10) NOT NULL,
    ve_consignmentnumber character varying(10) NOT NULL,
    ve_drivername character varying(30) NOT NULL,
    ve_drivernumber character varying(30) NOT NULL,
    ve_lastmodifiedby character varying(30) NOT NULL,
    ve_status_id bigint NOT NULL,
    ve_transportbusinesstype_id bigint NOT NULL,
    ve_vehiclenumber_id bigint NOT NULL,
    ve_vehiclesource_id bigint NOT NULL,
    ve_vehicletype_id bigint NOT NULL
);
 -   DROP TABLE public.sms_app_vehicledetailinfo;
       public         heap    postgres    false            J           1259    43978     sms_app_vehicledetailinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehicledetailinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_vehicledetailinfo_id_seq;
       public          postgres    false    331            �           0    0     sms_app_vehicledetailinfo_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_vehicledetailinfo_id_seq OWNED BY public.sms_app_vehicledetailinfo.id;
          public          postgres    false    330            I           1259    43970    sms_app_vehiclemasterinfo    TABLE     �  CREATE TABLE public.sms_app_vehiclemasterinfo (
    id bigint NOT NULL,
    vm_tonnage character varying(10) NOT NULL,
    vm_containersize character varying(10) NOT NULL,
    vm_capacity character varying(30) NOT NULL,
    vm_category character varying(30) NOT NULL,
    vm_registrationnumber character varying(30) NOT NULL,
    vm_millage character varying(30) NOT NULL,
    vm_cost character varying(30) NOT NULL,
    vm_yearofdepreciation character varying(30) NOT NULL,
    vm_ofdepreciation character varying(30) NOT NULL,
    vm_registrationdate character varying(30) NOT NULL,
    vm_valueofvehicle character varying(30) NOT NULL,
    vm_chassisnumber character varying(30) NOT NULL,
    vm_enginenumber integer NOT NULL,
    vm_batterynumber integer NOT NULL,
    vm_batterywarrantydate character varying(30) NOT NULL,
    vm_numberoftyres integer NOT NULL,
    vm_tyremake character varying(30) NOT NULL,
    vm_stephanietyremake character varying(30) NOT NULL,
    vm_stephanietyre character varying(30) NOT NULL,
    vm_tyre1 character varying(30) NOT NULL,
    vm_tyre2 character varying(30) NOT NULL,
    vm_tyre3 character varying(30) NOT NULL,
    vm_tyre4 character varying(30) NOT NULL,
    vm_fireextinguisher character varying(30) NOT NULL,
    vm_fireextexpirydate character varying(30) NOT NULL,
    vm_firstaidkit character varying(30) NOT NULL,
    vm_fakexpirydate character varying(30) NOT NULL,
    vm_gprstrackingid character varying(30) NOT NULL,
    vm_toolboxcontent1 character varying(30) NOT NULL,
    vm_toolboxcontent2 character varying(30) NOT NULL,
    vm_toolboxcontent3 character varying(30) NOT NULL,
    vm_toolboxcontent4 character varying(30) NOT NULL,
    vm_toolboxcontent5 character varying(30) NOT NULL,
    vm_gprssimid character varying(30) NOT NULL,
    vm_company character varying(30) NOT NULL,
    vm_policy character varying(30) NOT NULL,
    vm_policyexpirydate character varying(30) NOT NULL,
    vm_premium character varying(30) NOT NULL,
    vm_icvvalue character varying(30) NOT NULL,
    vm_ncb character varying(30) NOT NULL,
    vm_rtoname character varying(30) NOT NULL,
    vm_fcdate character varying(30) NOT NULL,
    vm_receipt character varying(30) NOT NULL,
    vm_fcamount character varying(30) NOT NULL,
    vm_fcexpirydate character varying(30) NOT NULL,
    vm_agencyname character varying(30) NOT NULL,
    vm_agencycharges character varying(30) NOT NULL,
    vm_roadtaxamount character varying(30) NOT NULL,
    vm_roadtaxexpirydate character varying(30) NOT NULL,
    vm_roadtaxreceipt character varying(30) NOT NULL,
    vm_roadtaxreceiptdate character varying(30) NOT NULL,
    vm_permitexpirydate character varying(30) NOT NULL,
    vm_permit character varying(30) NOT NULL,
    vm_permitamount character varying(30) NOT NULL,
    vm_permitdate character varying(30) NOT NULL,
    vm_pollutioncertificate character varying(30) NOT NULL,
    vm_pollutioncertificateamt character varying(30) NOT NULL,
    vm_pollutioncertificatedate character varying(30) NOT NULL,
    vm_mobileappdeviceid character varying(30) NOT NULL,
    vm_bpclcard character varying(30) NOT NULL,
    vm_fastagid character varying(30) NOT NULL,
    vm_primarydrivername character varying(30) NOT NULL,
    vm_primarydrivermob integer NOT NULL,
    vm_potenialrevenue character varying(30) NOT NULL,
    vm_secondarydrivername character varying(30) NOT NULL,
    vm_secondarydrivermob integer NOT NULL,
    vm_budgetexpense character varying(30) NOT NULL,
    vm_axletype_id bigint NOT NULL,
    vm_body_id bigint NOT NULL,
    vm_fccopy bigint NOT NULL,
    vm_fueltype_id bigint NOT NULL,
    vm_insurancecopy bigint NOT NULL,
    vm_insurancetype_id bigint NOT NULL,
    vm_ownership_id bigint NOT NULL,
    vm_permitcopy bigint NOT NULL,
    vm_permittype_id bigint NOT NULL,
    vm_pollutioncertificatecopy bigint NOT NULL,
    vm_roadtaxcopy bigint NOT NULL,
    vm_vehiclecolour_id bigint NOT NULL,
    vm_vehiclemanufacturer_id bigint NOT NULL,
    vm_vehiclemodel_id bigint NOT NULL,
    vm_vehicletype_id bigint NOT NULL
);
 -   DROP TABLE public.sms_app_vehiclemasterinfo;
       public         heap    postgres    false            H           1259    43969     sms_app_vehiclemasterinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehiclemasterinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_vehiclemasterinfo_id_seq;
       public          postgres    false    329            �           0    0     sms_app_vehiclemasterinfo_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_vehiclemasterinfo_id_seq OWNED BY public.sms_app_vehiclemasterinfo.id;
          public          postgres    false    328            5           1259    43896    sms_app_vehiclemodelinfo    TABLE     u   CREATE TABLE public.sms_app_vehiclemodelinfo (
    id bigint NOT NULL,
    vl_vehiclemodel character varying(100)
);
 ,   DROP TABLE public.sms_app_vehiclemodelinfo;
       public         heap    postgres    false            4           1259    43895    sms_app_vehiclemodelinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehiclemodelinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.sms_app_vehiclemodelinfo_id_seq;
       public          postgres    false    309            �           0    0    sms_app_vehiclemodelinfo_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.sms_app_vehiclemodelinfo_id_seq OWNED BY public.sms_app_vehiclemodelinfo.id;
          public          postgres    false    308            7           1259    43903    sms_app_vehiclenumberinfo    TABLE     w   CREATE TABLE public.sms_app_vehiclenumberinfo (
    id bigint NOT NULL,
    vn_vehiclenumber character varying(100)
);
 -   DROP TABLE public.sms_app_vehiclenumberinfo;
       public         heap    postgres    false            6           1259    43902     sms_app_vehiclenumberinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehiclenumberinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_vehiclenumberinfo_id_seq;
       public          postgres    false    311            �           0    0     sms_app_vehiclenumberinfo_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_vehiclenumberinfo_id_seq OWNED BY public.sms_app_vehiclenumberinfo.id;
          public          postgres    false    310            9           1259    43910    sms_app_vehiclesourceinfo    TABLE     w   CREATE TABLE public.sms_app_vehiclesourceinfo (
    id bigint NOT NULL,
    vs_vehiclesource character varying(100)
);
 -   DROP TABLE public.sms_app_vehiclesourceinfo;
       public         heap    postgres    false            8           1259    43909     sms_app_vehiclesourceinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehiclesourceinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_vehiclesourceinfo_id_seq;
       public          postgres    false    313            �           0    0     sms_app_vehiclesourceinfo_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_vehiclesourceinfo_id_seq OWNED BY public.sms_app_vehiclesourceinfo.id;
          public          postgres    false    312            ;           1259    43917    sms_app_vehicletypeinfo    TABLE     s   CREATE TABLE public.sms_app_vehicletypeinfo (
    id bigint NOT NULL,
    vt_vehicletype character varying(100)
);
 +   DROP TABLE public.sms_app_vehicletypeinfo;
       public         heap    postgres    false            :           1259    43916    sms_app_vehicletypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vehicletypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.sms_app_vehicletypeinfo_id_seq;
       public          postgres    false    315            �           0    0    sms_app_vehicletypeinfo_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.sms_app_vehicletypeinfo_id_seq OWNED BY public.sms_app_vehicletypeinfo.id;
          public          postgres    false    314            G           1259    43961    sms_app_vendor_info    TABLE     �  CREATE TABLE public.sms_app_vendor_info (
    id bigint NOT NULL,
    vend_name character varying(100) NOT NULL,
    vend_description character varying(100) NOT NULL,
    vend_contact character varying(10) NOT NULL,
    vend_contact_per character varying(50) NOT NULL,
    vend_gstin character varying(10) NOT NULL,
    vend_designation character varying(30) NOT NULL,
    vend_email character varying(50) NOT NULL,
    vend_zip character varying(10) NOT NULL,
    vend_address character varying(300) NOT NULL,
    vend_city_id bigint NOT NULL,
    vend_country_id bigint NOT NULL,
    vend_state_id bigint NOT NULL,
    vend_status_id bigint NOT NULL
);
 '   DROP TABLE public.sms_app_vendor_info;
       public         heap    postgres    false            F           1259    43960    sms_app_vendor_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vendor_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.sms_app_vendor_info_id_seq;
       public          postgres    false    327            �           0    0    sms_app_vendor_info_id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.sms_app_vendor_info_id_seq OWNED BY public.sms_app_vendor_info.id;
          public          postgres    false    326            =           1259    43924    sms_app_vhmanufacturerinfo    TABLE     y   CREATE TABLE public.sms_app_vhmanufacturerinfo (
    id bigint NOT NULL,
    vr_vhmanufacturer character varying(100)
);
 .   DROP TABLE public.sms_app_vhmanufacturerinfo;
       public         heap    postgres    false            <           1259    43923 !   sms_app_vhmanufacturerinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_vhmanufacturerinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 8   DROP SEQUENCE public.sms_app_vhmanufacturerinfo_id_seq;
       public          postgres    false    317            �           0    0 !   sms_app_vhmanufacturerinfo_id_seq    SEQUENCE OWNED BY     g   ALTER SEQUENCE public.sms_app_vhmanufacturerinfo_id_seq OWNED BY public.sms_app_vhmanufacturerinfo.id;
          public          postgres    false    316            E           1259    43954    sms_app_warehouse_goods_info    TABLE     �  CREATE TABLE public.sms_app_warehouse_goods_info (
    id bigint NOT NULL,
    wh_job_no character varying(20) NOT NULL,
    wh_goods_invoice character varying(20),
    wh_goods_pieces double precision NOT NULL,
    wh_goods_length double precision NOT NULL,
    wh_goods_width double precision NOT NULL,
    wh_goods_height double precision NOT NULL,
    wh_goods_weight double precision NOT NULL,
    wh_goods_volume_weight double precision NOT NULL,
    wh_uom bigint,
    wh_chargeable_weight double precision,
    "wh_CBM" double precision,
    wh_available_area double precision,
    wh_available_volume double precision,
    wh_goods_area double precision,
    wh_customer_name character varying(20),
    wh_customer_type character varying(20),
    wh_bay_id bigint,
    wh_branch_id bigint,
    wh_check_in_out bigint,
    wh_damages bigint,
    wh_dimension_deviation bigint,
    wh_goods_package_type_id bigint NOT NULL,
    wh_goods_status bigint,
    wh_mismatches bigint,
    wh_no_of_units_deviation bigint,
    wh_ratification_process bigint,
    wh_unit_id bigint,
    wh_weights_deviation bigint,
    wh_stack_layer_id bigint,
    wh_checkin_time timestamp with time zone NOT NULL,
    wh_qr_rand_num character varying(20),
    wh_dispatch_num character varying(20),
    wh_consignee character varying(20),
    wh_consigner character varying(20),
    wh_checkout_time timestamp with time zone,
    wh_storage_time character varying(50)
);
 0   DROP TABLE public.sms_app_warehouse_goods_info;
       public         heap    postgres    false            D           1259    43953 #   sms_app_warehouse_goods_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_warehouse_goods_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 :   DROP SEQUENCE public.sms_app_warehouse_goods_info_id_seq;
       public          postgres    false    325            �           0    0 #   sms_app_warehouse_goods_info_id_seq    SEQUENCE OWNED BY     k   ALTER SEQUENCE public.sms_app_warehouse_goods_info_id_seq OWNED BY public.sms_app_warehouse_goods_info.id;
          public          postgres    false    324            C           1259    43945    sms_app_warehouse_stock_info    TABLE     �  CREATE TABLE public.sms_app_warehouse_stock_info (
    id bigint NOT NULL,
    wh_stock_invoice character varying(20) NOT NULL,
    wh_stock_customer_name character varying(20) NOT NULL,
    wh_stock_arrival_date character varying(20),
    wh_stock_unloading_start_time character varying(20),
    wh_stock_unloading_end_time character varying(20),
    "wh_stock_FRD_time" character varying(20),
    wh_stock_invoice_value integer,
    wh_stock_amount_in integer,
    wh_stock_transporters character varying(100),
    wh_stock_truck_number character varying(20),
    wh_stock_truck_type character varying(20),
    wh_stock_consigner_name character varying(100),
    wh_stock_consignee_name character varying(100),
    wh_stock_docs_received character varying(10),
    "wh_stock_HAWB" character varying(20),
    "wh_stock_MAWB" character varying(20),
    wh_stock_destination character varying(30),
    wh_stock_case_number character varying(20),
    wh_stock_invoice_weight integer,
    "wh_stock_CBM" character varying(20),
    wh_stock_eway_bill character varying(20),
    wh_stock_fumigation_status character varying(20),
    wh_stock_location character varying(20),
    wh_stock_days_in_wh integer,
    wh_stock_ship_date character varying(20),
    wh_stock_out_time character varying(20),
    wh_stock_labels_pasted_by character varying(20),
    wh_stock_remarks character varying(250),
    wh_stock_driver_name character varying(250),
    wh_stock_driver_contact character varying(250),
    wh_stock_driver_lic character varying(250),
    wh_stock_driver_name_out character varying(250),
    wh_stock_driver_contact_out character varying(250),
    wh_stock_driver_lic_out character varying(250),
    wh_stock_arrival_date_out character varying(20),
    wh_stock_unloading_start_time_out character varying(20),
    wh_stock_unloading_end_time_out character varying(20),
    "wh_stock_FRD_time_out" character varying(20),
    wh_stock_transporters_out character varying(100),
    wh_stock_truck_number_out character varying(20),
    wh_stock_truck_type_out character varying(20),
    wh_stock_invoice_currency_id bigint,
    wh_stock_movement_type_id bigint,
    wh_stock_type_id bigint
);
 0   DROP TABLE public.sms_app_warehouse_stock_info;
       public         heap    postgres    false            B           1259    43944 #   sms_app_warehouse_stock_info_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_warehouse_stock_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 :   DROP SEQUENCE public.sms_app_warehouse_stock_info_id_seq;
       public          postgres    false    323            �           0    0 #   sms_app_warehouse_stock_info_id_seq    SEQUENCE OWNED BY     k   ALTER SEQUENCE public.sms_app_warehouse_stock_info_id_seq OWNED BY public.sms_app_warehouse_stock_info.id;
          public          postgres    false    322            A           1259    43938    sms_app_whratemasterinfo    TABLE     m  CREATE TABLE public.sms_app_whratemasterinfo (
    id bigint NOT NULL,
    whrm_customer_name character varying(20),
    whrm_storage_charge integer NOT NULL,
    whrm_loading_charge integer NOT NULL,
    whrm_unloading_charge integer NOT NULL,
    whrm_forkliftloading_charge integer NOT NULL,
    whrm_forkliftunloading_charge integer NOT NULL,
    whrm_crane_loading_charge integer NOT NULL,
    whrm_crane_unloading_charge integer NOT NULL,
    whrm_over_time_charge integer NOT NULL,
    whrm_insurance_charge integer NOT NULL,
    whrm_addmanpow_charge integer NOT NULL,
    whrm_storage_type_id bigint NOT NULL
);
 ,   DROP TABLE public.sms_app_whratemasterinfo;
       public         heap    postgres    false            @           1259    43937    sms_app_whratemasterinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_whratemasterinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public.sms_app_whratemasterinfo_id_seq;
       public          postgres    false    321            �           0    0    sms_app_whratemasterinfo_id_seq    SEQUENCE OWNED BY     c   ALTER SEQUENCE public.sms_app_whratemasterinfo_id_seq OWNED BY public.sms_app_whratemasterinfo.id;
          public          postgres    false    320            ?           1259    43931    sms_app_whstoragetypeinfo    TABLE     {   CREATE TABLE public.sms_app_whstoragetypeinfo (
    id bigint NOT NULL,
    "Whstoragetype_name" character varying(100)
);
 -   DROP TABLE public.sms_app_whstoragetypeinfo;
       public         heap    postgres    false            >           1259    43930     sms_app_whstoragetypeinfo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.sms_app_whstoragetypeinfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.sms_app_whstoragetypeinfo_id_seq;
       public          postgres    false    319            �           0    0     sms_app_whstoragetypeinfo_id_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.sms_app_whstoragetypeinfo_id_seq OWNED BY public.sms_app_whstoragetypeinfo.id;
          public          postgres    false    318                       2604    43489    auth_group id    DEFAULT     n   ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);
 <   ALTER TABLE public.auth_group ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    215    216    216                       2604    43498    auth_group_permissions id    DEFAULT     �   ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);
 H   ALTER TABLE public.auth_group_permissions ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    217    218    218                       2604    43482    auth_permission id    DEFAULT     x   ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);
 A   ALTER TABLE public.auth_permission ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    214    213    214            	           2604    43505    auth_user id    DEFAULT     l   ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);
 ;   ALTER TABLE public.auth_user ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    220    219    220            
           2604    43514    auth_user_groups id    DEFAULT     z   ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);
 B   ALTER TABLE public.auth_user_groups ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    221    222    222                       2604    43521    auth_user_user_permissions id    DEFAULT     �   ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);
 L   ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    224    223    224                       2604    43580    django_admin_log id    DEFAULT     z   ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);
 B   ALTER TABLE public.django_admin_log ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    225    226    226                       2604    43473    django_content_type id    DEFAULT     �   ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);
 E   ALTER TABLE public.django_content_type ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    212    211    212                       2604    43464    django_migrations id    DEFAULT     |   ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);
 C   ALTER TABLE public.django_migrations ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    210    209    210            V           2604    45142    sms_app_activeinactiveinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_activeinactiveinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_activeinactiveinfo_id_seq'::regclass);
 L   ALTER TABLE public.sms_app_activeinactiveinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    372    373    373                       2604    43619    sms_app_assetinfo id    DEFAULT     |   ALTER TABLE ONLY public.sms_app_assetinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_assetinfo_id_seq'::regclass);
 C   ALTER TABLE public.sms_app_assetinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    229    228    229            P           2604    44161    sms_app_assign_asset_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_assign_asset_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_assign_asset_info_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_assign_asset_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    360    361    361                       2604    43626    sms_app_axletypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_axletypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_axletypeinfo_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_axletypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    230    231    231                       2604    43633    sms_app_bayinfo id    DEFAULT     x   ALTER TABLE ONLY public.sms_app_bayinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_bayinfo_id_seq'::regclass);
 A   ALTER TABLE public.sms_app_bayinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    233    232    233                       2604    43640    sms_app_bodyinfo id    DEFAULT     z   ALTER TABLE ONLY public.sms_app_bodyinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_bodyinfo_id_seq'::regclass);
 B   ALTER TABLE public.sms_app_bodyinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    234    235    235            Q           2604    44888    sms_app_check_in_out id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_check_in_out ALTER COLUMN id SET DEFAULT nextval('public.sms_app_check_in_out_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_check_in_out ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    363    362    363                       2604    43647    sms_app_city id    DEFAULT     r   ALTER TABLE ONLY public.sms_app_city ALTER COLUMN id SET DEFAULT nextval('public.sms_app_city_id_seq'::regclass);
 >   ALTER TABLE public.sms_app_city ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    237    236    237            O           2604    44134     sms_app_consignmentdetailinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_consignmentdetailinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_consignmentdetailinfo_id_seq'::regclass);
 O   ALTER TABLE public.sms_app_consignmentdetailinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    359    358    359                       2604    43654    sms_app_country id    DEFAULT     x   ALTER TABLE ONLY public.sms_app_country ALTER COLUMN id SET DEFAULT nextval('public.sms_app_country_id_seq'::regclass);
 A   ALTER TABLE public.sms_app_country ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    239    238    239                       2604    43661    sms_app_crcountfrominfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_crcountfrominfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_crcountfrominfo_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_crcountfrominfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    241    240    241                       2604    43668    sms_app_currency_type id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_currency_type ALTER COLUMN id SET DEFAULT nextval('public.sms_app_currency_type_id_seq'::regclass);
 G   ALTER TABLE public.sms_app_currency_type ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    242    243    243                       2604    43675 !   sms_app_customerdepartmentinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_customerdepartmentinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_customerdepartmentinfo_id_seq'::regclass);
 P   ALTER TABLE public.sms_app_customerdepartmentinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    244    245    245                       2604    43682    sms_app_customerinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_customerinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_customerinfo_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_customerinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    246    247    247                       2604    43689    sms_app_customernameinfo_new id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_customernameinfo_new ALTER COLUMN id SET DEFAULT nextval('public.sms_app_customernameinfo_new_id_seq'::regclass);
 N   ALTER TABLE public.sms_app_customernameinfo_new ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    248    249    249                       2604    43696    sms_app_customertypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_customertypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_customertypeinfo_id_seq'::regclass);
 J   ALTER TABLE public.sms_app_customertypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    251    250    251                       2604    43703    sms_app_damageinfo id    DEFAULT     ~   ALTER TABLE ONLY public.sms_app_damageinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_damageinfo_id_seq'::regclass);
 D   ALTER TABLE public.sms_app_damageinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    253    252    253            U           2604    45111    sms_app_damagereportimages id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_damagereportimages ALTER COLUMN id SET DEFAULT nextval('public.sms_app_damagereportimages_id_seq'::regclass);
 L   ALTER TABLE public.sms_app_damagereportimages ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    370    371    371            N           2604    44092    sms_app_damagereportinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_damagereportinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_damagereportinfo_id_seq'::regclass);
 J   ALTER TABLE public.sms_app_damagereportinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    357    356    357                       2604    43710    sms_app_department_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_department_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_department_info_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_department_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    254    255    255                       2604    43717    sms_app_designationinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_designationinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_designationinfo_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_designationinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    257    256    257            X           2604    45207    sms_app_dispatch_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_dispatch_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_dispatch_info_id_seq'::regclass);
 G   ALTER TABLE public.sms_app_dispatch_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    377    376    377            M           2604    44078    sms_app_employee id    DEFAULT     z   ALTER TABLE ONLY public.sms_app_employee ALTER COLUMN id SET DEFAULT nextval('public.sms_app_employee_id_seq'::regclass);
 B   ALTER TABLE public.sms_app_employee ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    355    354    355                       2604    43724    sms_app_enquiry_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_enquiry_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_enquiry_info_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_enquiry_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    259    258    259            L           2604    44071    sms_app_enquirynoteinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_enquirynoteinfo_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_enquirynoteinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    353    352    353                       2604    43731    sms_app_fueltypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_fueltypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_fueltypeinfo_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_fueltypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    261    260    261            K           2604    44064    sms_app_gatein_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_gatein_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_gatein_info_id_seq'::regclass);
 E   ALTER TABLE public.sms_app_gatein_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    351    350    351                       2604    43738    sms_app_gstexcemptioninfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_gstexcemptioninfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_gstexcemptioninfo_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_gstexcemptioninfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    263    262    263                        2604    43745    sms_app_gstmodelinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_gstmodelinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_gstmodelinfo_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_gstmodelinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    265    264    265            J           2604    44057    sms_app_insurance_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_insurance_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_insurance_info_id_seq'::regclass);
 H   ALTER TABLE public.sms_app_insurance_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    348    349    349            !           2604    43752    sms_app_insurance_type id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_insurance_type ALTER COLUMN id SET DEFAULT nextval('public.sms_app_insurance_type_id_seq'::regclass);
 H   ALTER TABLE public.sms_app_insurance_type ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    267    266    267            I           2604    44050    sms_app_loadingbay_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_loadingbay_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_loadingbay_info_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_loadingbay_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    347    346    347            Y           2604    45303     sms_app_loadingbayimages_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_loadingbayimages_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_loadingbayimages_info_id_seq'::regclass);
 O   ALTER TABLE public.sms_app_loadingbayimages_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    379    378    379            "           2604    43759    sms_app_location_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_location_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_location_info_id_seq'::regclass);
 G   ALTER TABLE public.sms_app_location_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    269    268    269            H           2604    44033    sms_app_locationmasterinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_locationmasterinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_locationmasterinfo_id_seq'::regclass);
 L   ALTER TABLE public.sms_app_locationmasterinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    344    345    345            #           2604    43766     sms_app_materialhandling_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_materialhandling_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_materialhandling_info_id_seq'::regclass);
 O   ALTER TABLE public.sms_app_materialhandling_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    271    270    271            $           2604    43773    sms_app_movementtypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_movementtypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_movementtypeinfo_id_seq'::regclass);
 J   ALTER TABLE public.sms_app_movementtypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    273    272    273            %           2604    43780    sms_app_ownershipinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_ownershipinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_ownershipinfo_id_seq'::regclass);
 G   ALTER TABLE public.sms_app_ownershipinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    275    274    275            &           2604    43787    sms_app_packagetype_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_packagetype_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_packagetype_info_id_seq'::regclass);
 J   ALTER TABLE public.sms_app_packagetype_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    277    276    277            '           2604    43794    sms_app_paymenttypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_paymenttypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_paymenttypeinfo_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_paymenttypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    279    278    279            (           2604    43801    sms_app_peo_reg id    DEFAULT     x   ALTER TABLE ONLY public.sms_app_peo_reg ALTER COLUMN id SET DEFAULT nextval('public.sms_app_peo_reg_id_seq'::regclass);
 A   ALTER TABLE public.sms_app_peo_reg ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    281    280    281            )           2604    43808    sms_app_permittypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_permittypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_permittypeinfo_id_seq'::regclass);
 H   ALTER TABLE public.sms_app_permittypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    283    282    283            *           2604    43815    sms_app_prod_cat id    DEFAULT     z   ALTER TABLE ONLY public.sms_app_prod_cat ALTER COLUMN id SET DEFAULT nextval('public.sms_app_prod_cat_id_seq'::regclass);
 B   ALTER TABLE public.sms_app_prod_cat ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    285    284    285            +           2604    43822    sms_app_prod_type id    DEFAULT     |   ALTER TABLE ONLY public.sms_app_prod_type ALTER COLUMN id SET DEFAULT nextval('public.sms_app_prod_type_id_seq'::regclass);
 C   ALTER TABLE public.sms_app_prod_type ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    287    286    287            G           2604    44026    sms_app_product_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_product_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_product_info_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_product_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    343    342    343            S           2604    45048    sms_app_received_not id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_received_not ALTER COLUMN id SET DEFAULT nextval('public.sms_app_received_not_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_received_not ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    366    367    367            ,           2604    43829    sms_app_roleinfo id    DEFAULT     z   ALTER TABLE ONLY public.sms_app_roleinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_roleinfo_id_seq'::regclass);
 B   ALTER TABLE public.sms_app_roleinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    289    288    289            F           2604    44019    sms_app_rtratemasterinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_rtratemasterinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_rtratemasterinfo_id_seq'::regclass);
 J   ALTER TABLE public.sms_app_rtratemasterinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    341    340    341            E           2604    44012    sms_app_service_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_service_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_service_info_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_service_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    339    338    339            W           2604    45194    sms_app_stackinginfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_stackinginfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_stackinginfo_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_stackinginfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    374    375    375            -           2604    43836    sms_app_state id    DEFAULT     t   ALTER TABLE ONLY public.sms_app_state ALTER COLUMN id SET DEFAULT nextval('public.sms_app_state_id_seq'::regclass);
 ?   ALTER TABLE public.sms_app_state ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    291    290    291            .           2604    43843    sms_app_statuslist id    DEFAULT     ~   ALTER TABLE ONLY public.sms_app_statuslist ALTER COLUMN id SET DEFAULT nextval('public.sms_app_statuslist_id_seq'::regclass);
 D   ALTER TABLE public.sms_app_statuslist ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    293    292    293            /           2604    43850    sms_app_stock_movement_type id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_stock_movement_type ALTER COLUMN id SET DEFAULT nextval('public.sms_app_stock_movement_type_id_seq'::regclass);
 M   ALTER TABLE public.sms_app_stock_movement_type ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    295    294    295            0           2604    43857    sms_app_stock_type id    DEFAULT     ~   ALTER TABLE ONLY public.sms_app_stock_type ALTER COLUMN id SET DEFAULT nextval('public.sms_app_stock_type_id_seq'::regclass);
 D   ALTER TABLE public.sms_app_stock_type ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    297    296    297            1           2604    43864    sms_app_stud_reg id    DEFAULT     z   ALTER TABLE ONLY public.sms_app_stud_reg ALTER COLUMN id SET DEFAULT nextval('public.sms_app_stud_reg_id_seq'::regclass);
 B   ALTER TABLE public.sms_app_stud_reg ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    299    298    299            2           2604    43871    sms_app_trbusinesstypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_trbusinesstypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_trbusinesstypeinfo_id_seq'::regclass);
 L   ALTER TABLE public.sms_app_trbusinesstypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    300    301    301            D           2604    44005    sms_app_tripclosureinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_tripclosureinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_tripclosureinfo_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_tripclosureinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    336    337    337            C           2604    43998    sms_app_tripdetailinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_tripdetailinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_tripdetailinfo_id_seq'::regclass);
 H   ALTER TABLE public.sms_app_tripdetailinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    335    334    335            3           2604    43878    sms_app_unitinfo id    DEFAULT     z   ALTER TABLE ONLY public.sms_app_unitinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_unitinfo_id_seq'::regclass);
 B   ALTER TABLE public.sms_app_unitinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    302    303    303            R           2604    44912    sms_app_uom id    DEFAULT     p   ALTER TABLE ONLY public.sms_app_uom ALTER COLUMN id SET DEFAULT nextval('public.sms_app_uom_id_seq'::regclass);
 =   ALTER TABLE public.sms_app_uom ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    365    364    365            T           2604    45065    sms_app_uploadinfo id    DEFAULT     ~   ALTER TABLE ONLY public.sms_app_uploadinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_uploadinfo_id_seq'::regclass);
 D   ALTER TABLE public.sms_app_uploadinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    369    368    369            B           2604    43989    sms_app_user_extinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_user_extinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_user_extinfo_id_seq'::regclass);
 F   ALTER TABLE public.sms_app_user_extinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    332    333    333            4           2604    43885    sms_app_vehiclecategoryinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehiclecategoryinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehiclecategoryinfo_id_seq'::regclass);
 M   ALTER TABLE public.sms_app_vehiclecategoryinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    304    305    305            5           2604    43892    sms_app_vehiclecolourinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehiclecolourinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehiclecolourinfo_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_vehiclecolourinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    307    306    307            A           2604    43982    sms_app_vehicledetailinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehicledetailinfo_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_vehicledetailinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    331    330    331            @           2604    43973    sms_app_vehiclemasterinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehiclemasterinfo_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_vehiclemasterinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    329    328    329            6           2604    43899    sms_app_vehiclemodelinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehiclemodelinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehiclemodelinfo_id_seq'::regclass);
 J   ALTER TABLE public.sms_app_vehiclemodelinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    309    308    309            7           2604    43906    sms_app_vehiclenumberinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehiclenumberinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehiclenumberinfo_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_vehiclenumberinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    311    310    311            8           2604    43913    sms_app_vehiclesourceinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehiclesourceinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehiclesourceinfo_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_vehiclesourceinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    312    313    313            9           2604    43920    sms_app_vehicletypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vehicletypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vehicletypeinfo_id_seq'::regclass);
 I   ALTER TABLE public.sms_app_vehicletypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    314    315    315            ?           2604    43964    sms_app_vendor_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vendor_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vendor_info_id_seq'::regclass);
 E   ALTER TABLE public.sms_app_vendor_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    327    326    327            :           2604    43927    sms_app_vhmanufacturerinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_vhmanufacturerinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_vhmanufacturerinfo_id_seq'::regclass);
 L   ALTER TABLE public.sms_app_vhmanufacturerinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    316    317    317            >           2604    43957    sms_app_warehouse_goods_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_warehouse_goods_info_id_seq'::regclass);
 N   ALTER TABLE public.sms_app_warehouse_goods_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    324    325    325            =           2604    43948    sms_app_warehouse_stock_info id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_warehouse_stock_info ALTER COLUMN id SET DEFAULT nextval('public.sms_app_warehouse_stock_info_id_seq'::regclass);
 N   ALTER TABLE public.sms_app_warehouse_stock_info ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    322    323    323            <           2604    43941    sms_app_whratemasterinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_whratemasterinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_whratemasterinfo_id_seq'::regclass);
 J   ALTER TABLE public.sms_app_whratemasterinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    320    321    321            ;           2604    43934    sms_app_whstoragetypeinfo id    DEFAULT     �   ALTER TABLE ONLY public.sms_app_whstoragetypeinfo ALTER COLUMN id SET DEFAULT nextval('public.sms_app_whstoragetypeinfo_id_seq'::regclass);
 K   ALTER TABLE public.sms_app_whstoragetypeinfo ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    319    318    319            �          0    43486 
   auth_group 
   TABLE DATA           .   COPY public.auth_group (id, name) FROM stdin;
    public          postgres    false    216   �3      �          0    43495    auth_group_permissions 
   TABLE DATA           M   COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
    public          postgres    false    218   4      �          0    43479    auth_permission 
   TABLE DATA           N   COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
    public          postgres    false    214   /4      �          0    43502 	   auth_user 
   TABLE DATA           �   COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
    public          postgres    false    220   �@      �          0    43511    auth_user_groups 
   TABLE DATA           A   COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
    public          postgres    false    222   *B      �          0    43518    auth_user_user_permissions 
   TABLE DATA           P   COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
    public          postgres    false    224   GB      �          0    43577    django_admin_log 
   TABLE DATA           �   COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
    public          postgres    false    226   dB      �          0    43470    django_content_type 
   TABLE DATA           C   COPY public.django_content_type (id, app_label, model) FROM stdin;
    public          postgres    false    212   �E      �          0    43461    django_migrations 
   TABLE DATA           C   COPY public.django_migrations (id, app, name, applied) FROM stdin;
    public          postgres    false    210   �H      �          0    43606    django_session 
   TABLE DATA           P   COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
    public          postgres    false    227   OR      P          0    45139    sms_app_activeinactiveinfo 
   TABLE DATA           I   COPY public.sms_app_activeinactiveinfo (id, active_inactive) FROM stdin;
    public          postgres    false    373   �W      �          0    43616    sms_app_assetinfo 
   TABLE DATA           &  COPY public.sms_app_assetinfo (id, asset_number, asset_model, asset_make, asset_serial_num1, asset_assignedon, asset_cost, asset_order_number, asset_purchase_date, asset_assignedto_id, asset_insurance_details_id, asset_location_id, asset_product_id, asset_unit_id, asset_vendor_id) FROM stdin;
    public          postgres    false    229   �W      D          0    44158    sms_app_assign_asset_info 
   TABLE DATA           �   COPY public.sms_app_assign_asset_info (id, "AA_assingedto", "AA_assignedon", "AA_assignedby", "AA_remarks", "AA_asset_number_id") FROM stdin;
    public          postgres    false    361   X      �          0    43623    sms_app_axletypeinfo 
   TABLE DATA           ?   COPY public.sms_app_axletypeinfo (id, at_axletype) FROM stdin;
    public          postgres    false    231   !X      �          0    43630    sms_app_bayinfo 
   TABLE DATA           b   COPY public.sms_app_bayinfo (id, bay_bayname, "Bay_unit_name_id", bay_branch_name_id) FROM stdin;
    public          postgres    false    233   >X      �          0    43637    sms_app_bodyinfo 
   TABLE DATA           7   COPY public.sms_app_bodyinfo (id, bo_body) FROM stdin;
    public          postgres    false    235   oX      F          0    44885    sms_app_check_in_out 
   TABLE DATA           E   COPY public.sms_app_check_in_out (id, check_in_out_name) FROM stdin;
    public          postgres    false    363   �X      �          0    43644    sms_app_city 
   TABLE DATA           K   COPY public.sms_app_city (id, city_name, country_id, state_id) FROM stdin;
    public          postgres    false    237   �X      B          0    44131    sms_app_consignmentdetailinfo 
   TABLE DATA           k  COPY public.sms_app_consignmentdetailinfo (id, co_enquirynumber, co_consignmentnumber, co_consignmentdate, co_consigner, co_consignee, co_consignerinvoice, co_consignervalue, co_valueininr, co_noofpieces, co_weight, co_ebillno, co_dateofissue, co_dateofvalidity, co_containerdescription, co_dimension, co_lastmodifiedby, co_movement_id, co_status_id) FROM stdin;
    public          postgres    false    359   Y      �          0    43651    sms_app_country 
   TABLE DATA           ;   COPY public.sms_app_country (id, country_name) FROM stdin;
    public          postgres    false    239   /Y      �          0    43658    sms_app_crcountfrominfo 
   TABLE DATA           E   COPY public.sms_app_crcountfrominfo (id, cf_crcountfrom) FROM stdin;
    public          postgres    false    241   ZY      �          0    43665    sms_app_currency_type 
   TABLE DATA           U   COPY public.sms_app_currency_type (id, currency_type, converision_value) FROM stdin;
    public          postgres    false    243   �Y      �          0    43672    sms_app_customerdepartmentinfo 
   TABLE DATA           S   COPY public.sms_app_customerdepartmentinfo (id, ct_customerdepartment) FROM stdin;
    public          postgres    false    245   �Y      �          0    43679    sms_app_customerinfo 
   TABLE DATA           �  COPY public.sms_app_customerinfo (id, cu_customercode, cu_name, cu_nameshort, cu_pan, cu_gst, cu_customerperson, cu_designation, cu_contactno, cu_email, cu_gstpercentage, cu_creditdays, cu_paymentcycle, cu_tallyid, cu_lastmodifiedby, cu_businessmodel_id, cu_creditcountfrom_id, cu_department_id, cu_gstexcepmtion_id, cu_gstmodel_id, cu_paymenttype_id, cu_state_id, cu_type_id) FROM stdin;
    public          postgres    false    247   Z      �          0    43686    sms_app_customernameinfo_new 
   TABLE DATA           K   COPY public.sms_app_customernameinfo_new (id, cn_customername) FROM stdin;
    public          postgres    false    249   �Z      �          0    43693    sms_app_customertypeinfo 
   TABLE DATA           J   COPY public.sms_app_customertypeinfo (id, cust_customer_type) FROM stdin;
    public          postgres    false    251   �Z      �          0    43700    sms_app_damageinfo 
   TABLE DATA           =   COPY public.sms_app_damageinfo (id, damage_name) FROM stdin;
    public          postgres    false    253   [      N          0    45108    sms_app_damagereportimages 
   TABLE DATA           �   COPY public.sms_app_damagereportimages (id, "dam_OTL_pic", damimage_wh_job_num, dam_document, dam_50_offload_pic, dam_closed_door_pic, dam_empty_vehicle, dam_open_door_pic) FROM stdin;
    public          postgres    false    371   l[      @          0    44089    sms_app_damagereportinfo 
   TABLE DATA           x   COPY public.sms_app_damagereportinfo (id, dam_wh_job_num, "dam_GRN_num", dam_damage_type_id, dam_status_id) FROM stdin;
    public          postgres    false    357   �\      �          0    43707    sms_app_department_info 
   TABLE DATA           P   COPY public.sms_app_department_info (id, dept_name, dept_status_id) FROM stdin;
    public          postgres    false    255   �\      �          0    43714    sms_app_designationinfo 
   TABLE DATA           K   COPY public.sms_app_designationinfo (id, des_designation_name) FROM stdin;
    public          postgres    false    257   F]      T          0    45204    sms_app_dispatch_info 
   TABLE DATA           �  COPY public.sms_app_dispatch_info (id, dispatch_depature_date, dispatch_driver, dispatch_contact_number, "dispatch_DL_number", dispatch_otl, dispatch_transporter, dispatch_truck_number, "dispatch_HAWB", "dispatch_MAWB", dispatch_destination, dispatch_comments, dispatch_cargo_picked, dispatch_status_id, "dispatch_sticker_pasted_BVM", dispatch_truck_type_id, dispatch_num) FROM stdin;
    public          postgres    false    377   �]      >          0    44075    sms_app_employee 
   TABLE DATA           �   COPY public.sms_app_employee (id, emp_empid, emp_full_name, emp_email, emp_contact, emp_designation, emp_branch, emp_password, emp_password_conf, emp_role, emp_status_id) FROM stdin;
    public          postgres    false    355   I^      �          0    43721    sms_app_enquiry_info 
   TABLE DATA           Y   COPY public.sms_app_enquiry_info (id, enq_enquiry_number, enq_customer_name) FROM stdin;
    public          postgres    false    259   f^      <          0    44068    sms_app_enquirynoteinfo 
   TABLE DATA           T  COPY public.sms_app_enquirynoteinfo (id, en_enquirynumber, en_othercustomer, en_customercode, en_customercontact, en_customeremail, en_raisedon, en_raisedby, en_lastmodifiedby, en_assignedto_id, en_customerdepartment_id, en_customername_id, en_fromlocaion, en_status_id, en_tolocation, en_vehiclecategory_id, en_vehicletype_id) FROM stdin;
    public          postgres    false    353   �^      �          0    43728    sms_app_fueltypeinfo 
   TABLE DATA           ?   COPY public.sms_app_fueltypeinfo (id, ft_fueltype) FROM stdin;
    public          postgres    false    261   �^      :          0    44061    sms_app_gatein_info 
   TABLE DATA           �  COPY public.sms_app_gatein_info (id, gatein_job_no, gatein_invoice, gatein_customer_type_id, gatein_arrival_date, gatein_shipper, gatein_consignee, gatein_no_of_pkg, gatein_weight, gatein_driver, gatein_contact_number, "gatein_DL_number", gatein_otl, gatein_transporter, gatein_truck_number, gatein_customer_id, gatein_status_id, gatein_truck_type_id, gatein_department_id, gatein_created_at, gatein_updated_at) FROM stdin;
    public          postgres    false    351   �^      �          0    43735    sms_app_gstexcemptioninfo 
   TABLE DATA           I   COPY public.sms_app_gstexcemptioninfo (id, ge_gstexcepmtion) FROM stdin;
    public          postgres    false    263   _`      �          0    43742    sms_app_gstmodelinfo 
   TABLE DATA           ?   COPY public.sms_app_gstmodelinfo (id, gm_gstmodel) FROM stdin;
    public          postgres    false    265   �`      8          0    44054    sms_app_insurance_info 
   TABLE DATA           �   COPY public.sms_app_insurance_info (id, ins_name, ins_start_date, ins_expiry_date, ins_units, ins_status_id, ins_type_id, ins_vendor_id) FROM stdin;
    public          postgres    false    349   �`      �          0    43749    sms_app_insurance_type 
   TABLE DATA           D   COPY public.sms_app_insurance_type (id, insurance_name) FROM stdin;
    public          postgres    false    267   �`      6          0    44047    sms_app_loadingbay_info 
   TABLE DATA           �  COPY public.sms_app_loadingbay_info (id, lb_job_no, lb_invoice, lb_eway_bill, lb_validity_date, lb_stock_unloading_start_time, lb_stock_unloading_end_time, "lb_stock_FRD_time", lb_stock_invoice_value, lb_stock_amount_in, lb_offload_acceptance, lb_otl_check, lb_packing_list, lb_status_id, lb_stock_invoice_currency_id, lb_stock_type_id, lb_stock_currency_con, lb_mh_crane, lb_mh_forklift, lb_mh_handtrolley, lb_mh_manual) FROM stdin;
    public          postgres    false    347   a      V          0    45300    sms_app_loadingbayimages_info 
   TABLE DATA           [   COPY public.sms_app_loadingbayimages_info (id, lbimg_job_no, lbimg_inward_pod) FROM stdin;
    public          postgres    false    379   �a      �          0    43756    sms_app_location_info 
   TABLE DATA           �   COPY public.sms_app_location_info (id, loc_name, loc_zipcode, loc_address, loc_city_id, loc_country_id, loc_state_id, loc_status_id) FROM stdin;
    public          postgres    false    269   �b      4          0    44030    sms_app_locationmasterinfo 
   TABLE DATA           -  COPY public.sms_app_locationmasterinfo (id, lm_length, lm_width, lm_height, lm_size, lm_area_occupied, lm_available_area, lm_total_volume, lm_available_volume, lm_volume_occupied, lm_concatenate, lm_customer_model_id, lm_areaside_id, lm_customer_name_id, lm_wh_location_id, lm_wh_unit_id) FROM stdin;
    public          postgres    false    345   c      �          0    43763    sms_app_materialhandling_info 
   TABLE DATA           F   COPY public.sms_app_materialhandling_info (id, "MH_name") FROM stdin;
    public          postgres    false    271   �c      �          0    43770    sms_app_movementtypeinfo 
   TABLE DATA           G   COPY public.sms_app_movementtypeinfo (id, mt_movementtype) FROM stdin;
    public          postgres    false    273   ?d      �          0    43777    sms_app_ownershipinfo 
   TABLE DATA           A   COPY public.sms_app_ownershipinfo (id, ow_ownership) FROM stdin;
    public          postgres    false    275   \d      �          0    43784    sms_app_packagetype_info 
   TABLE DATA           D   COPY public.sms_app_packagetype_info (id, package_type) FROM stdin;
    public          postgres    false    277   yd      �          0    43791    sms_app_paymenttypeinfo 
   TABLE DATA           E   COPY public.sms_app_paymenttypeinfo (id, pa_paymenttype) FROM stdin;
    public          postgres    false    279   �d      �          0    43798    sms_app_peo_reg 
   TABLE DATA           V   COPY public.sms_app_peo_reg (id, peo_name, peo_age, peo_mob, peo_address) FROM stdin;
    public          postgres    false    281   �d      �          0    43805    sms_app_permittypeinfo 
   TABLE DATA           C   COPY public.sms_app_permittypeinfo (id, pt_permittype) FROM stdin;
    public          postgres    false    283   e      �          0    43812    sms_app_prod_cat 
   TABLE DATA           >   COPY public.sms_app_prod_cat (id, prod_cat_title) FROM stdin;
    public          postgres    false    285   e      �          0    43819    sms_app_prod_type 
   TABLE DATA           @   COPY public.sms_app_prod_type (id, prod_type_title) FROM stdin;
    public          postgres    false    287   <e      2          0    44023    sms_app_product_info 
   TABLE DATA           ]   COPY public.sms_app_product_info (id, prod_name, prod_description, prod_type_id) FROM stdin;
    public          postgres    false    343   Ye      J          0    45045    sms_app_received_not 
   TABLE DATA           E   COPY public.sms_app_received_not (id, received_not_name) FROM stdin;
    public          postgres    false    367   ve      �          0    43826    sms_app_roleinfo 
   TABLE DATA           9   COPY public.sms_app_roleinfo (id, role_name) FROM stdin;
    public          postgres    false    289   �e      0          0    44016    sms_app_rtratemasterinfo 
   TABLE DATA           �   COPY public.sms_app_rtratemasterinfo (id, ro_rate, ro_customer_id, ro_customerdepartment_id, ro_fromlocation, ro_tolocation, ro_vehicletype) FROM stdin;
    public          postgres    false    341   �e      .          0    44009    sms_app_service_info 
   TABLE DATA           �   COPY public.sms_app_service_info (id, ser_start_date, ser_end_date, ser_cost, ser_asset_id, ser_status_id, ser_vendor_id) FROM stdin;
    public          postgres    false    339   �e      R          0    45191    sms_app_stackinginfo 
   TABLE DATA           ?   COPY public.sms_app_stackinginfo (id, stack_layer) FROM stdin;
    public          postgres    false    375   f      �          0    43833    sms_app_state 
   TABLE DATA           C   COPY public.sms_app_state (id, state_name, country_id) FROM stdin;
    public          postgres    false    291   <f                 0    43840    sms_app_statuslist 
   TABLE DATA           >   COPY public.sms_app_statuslist (id, status_title) FROM stdin;
    public          postgres    false    293   �f                0    43847    sms_app_stock_movement_type 
   TABLE DATA           I   COPY public.sms_app_stock_movement_type (id, stock_mov_type) FROM stdin;
    public          postgres    false    295   �f                0    43854    sms_app_stock_type 
   TABLE DATA           <   COPY public.sms_app_stock_type (id, stock_type) FROM stdin;
    public          postgres    false    297   �f                0    43861    sms_app_stud_reg 
   TABLE DATA              COPY public.sms_app_stud_reg (id, stud_name, stud_age, stud_eng, stud_tamil, stud_math, stud_social, stud_science) FROM stdin;
    public          postgres    false    299   0g                0    43868    sms_app_trbusinesstypeinfo 
   TABLE DATA           K   COPY public.sms_app_trbusinesstypeinfo (id, tb_trbusinesstype) FROM stdin;
    public          postgres    false    301   Mg      ,          0    44002    sms_app_tripclosureinfo 
   TABLE DATA           �   COPY public.sms_app_tripclosureinfo (id, tc_enquirynumber, tc_consignmentnumber, tc_tripcost, tc_parkingcost, tc_tollcost, tc_loadingcost, tc_unloadingcost, tc_lastmodifiedby, tc_financestatus_id) FROM stdin;
    public          postgres    false    337   �g      *          0    43995    sms_app_tripdetailinfo 
   TABLE DATA           R  COPY public.sms_app_tripdetailinfo (id, tr_enquirynumber, tr_consignmentnumber, tr_tripnumber, tr_startingkm, tr_startingdate, tr_deliveryimages, tr_proofofdelivery, tr_sealnumber, tr_containernumber, tr_endingkm, tr_endingdate, tr_shipmentdetails, tr_lastmodifiedby, tr_fromlocation, tr_status, tr_tolocation, tr_tripstatus) FROM stdin;
    public          postgres    false    335   �g      
          0    43875    sms_app_unitinfo 
   TABLE DATA           L   COPY public.sms_app_unitinfo (id, unit_name, ui_branch_name_id) FROM stdin;
    public          postgres    false    303   �g      H          0    44909    sms_app_uom 
   TABLE DATA           3   COPY public.sms_app_uom (id, uom_name) FROM stdin;
    public          postgres    false    365   h      L          0    45062    sms_app_uploadinfo 
   TABLE DATA           g   COPY public.sms_app_uploadinfo (id, file_upload_nam, image_upload_nam, upload_description) FROM stdin;
    public          postgres    false    369   0h      (          0    43986    sms_app_user_extinfo 
   TABLE DATA           �   COPY public.sms_app_user_extinfo (id, emp_contact, emp_pan, emp_uan, emp_esi, emp_aadhar, "emp_DOB", "emp_DOJ", department_id, emp_branch_id, emp_designation_id, emp_role_id, user_id) FROM stdin;
    public          postgres    false    333   i                0    43882    sms_app_vehiclecategoryinfo 
   TABLE DATA           M   COPY public.sms_app_vehiclecategoryinfo (id, vc_vehiclecategory) FROM stdin;
    public          postgres    false    305   ?i                0    43889    sms_app_vehiclecolourinfo 
   TABLE DATA           I   COPY public.sms_app_vehiclecolourinfo (id, vh_vehiclecolour) FROM stdin;
    public          postgres    false    307   \i      &          0    43979    sms_app_vehicledetailinfo 
   TABLE DATA           �   COPY public.sms_app_vehicledetailinfo (id, ve_enquirynumber, ve_consignmentnumber, ve_drivername, ve_drivernumber, ve_lastmodifiedby, ve_status_id, ve_transportbusinesstype_id, ve_vehiclenumber_id, ve_vehiclesource_id, ve_vehicletype_id) FROM stdin;
    public          postgres    false    331   yi      $          0    43970    sms_app_vehiclemasterinfo 
   TABLE DATA           �  COPY public.sms_app_vehiclemasterinfo (id, vm_tonnage, vm_containersize, vm_capacity, vm_category, vm_registrationnumber, vm_millage, vm_cost, vm_yearofdepreciation, vm_ofdepreciation, vm_registrationdate, vm_valueofvehicle, vm_chassisnumber, vm_enginenumber, vm_batterynumber, vm_batterywarrantydate, vm_numberoftyres, vm_tyremake, vm_stephanietyremake, vm_stephanietyre, vm_tyre1, vm_tyre2, vm_tyre3, vm_tyre4, vm_fireextinguisher, vm_fireextexpirydate, vm_firstaidkit, vm_fakexpirydate, vm_gprstrackingid, vm_toolboxcontent1, vm_toolboxcontent2, vm_toolboxcontent3, vm_toolboxcontent4, vm_toolboxcontent5, vm_gprssimid, vm_company, vm_policy, vm_policyexpirydate, vm_premium, vm_icvvalue, vm_ncb, vm_rtoname, vm_fcdate, vm_receipt, vm_fcamount, vm_fcexpirydate, vm_agencyname, vm_agencycharges, vm_roadtaxamount, vm_roadtaxexpirydate, vm_roadtaxreceipt, vm_roadtaxreceiptdate, vm_permitexpirydate, vm_permit, vm_permitamount, vm_permitdate, vm_pollutioncertificate, vm_pollutioncertificateamt, vm_pollutioncertificatedate, vm_mobileappdeviceid, vm_bpclcard, vm_fastagid, vm_primarydrivername, vm_primarydrivermob, vm_potenialrevenue, vm_secondarydrivername, vm_secondarydrivermob, vm_budgetexpense, vm_axletype_id, vm_body_id, vm_fccopy, vm_fueltype_id, vm_insurancecopy, vm_insurancetype_id, vm_ownership_id, vm_permitcopy, vm_permittype_id, vm_pollutioncertificatecopy, vm_roadtaxcopy, vm_vehiclecolour_id, vm_vehiclemanufacturer_id, vm_vehiclemodel_id, vm_vehicletype_id) FROM stdin;
    public          postgres    false    329   �i                0    43896    sms_app_vehiclemodelinfo 
   TABLE DATA           G   COPY public.sms_app_vehiclemodelinfo (id, vl_vehiclemodel) FROM stdin;
    public          postgres    false    309   �i                0    43903    sms_app_vehiclenumberinfo 
   TABLE DATA           I   COPY public.sms_app_vehiclenumberinfo (id, vn_vehiclenumber) FROM stdin;
    public          postgres    false    311   �i                0    43910    sms_app_vehiclesourceinfo 
   TABLE DATA           I   COPY public.sms_app_vehiclesourceinfo (id, vs_vehiclesource) FROM stdin;
    public          postgres    false    313   �i                0    43917    sms_app_vehicletypeinfo 
   TABLE DATA           E   COPY public.sms_app_vehicletypeinfo (id, vt_vehicletype) FROM stdin;
    public          postgres    false    315   
j      "          0    43961    sms_app_vendor_info 
   TABLE DATA           �   COPY public.sms_app_vendor_info (id, vend_name, vend_description, vend_contact, vend_contact_per, vend_gstin, vend_designation, vend_email, vend_zip, vend_address, vend_city_id, vend_country_id, vend_state_id, vend_status_id) FROM stdin;
    public          postgres    false    327   Cj                0    43924    sms_app_vhmanufacturerinfo 
   TABLE DATA           K   COPY public.sms_app_vhmanufacturerinfo (id, vr_vhmanufacturer) FROM stdin;
    public          postgres    false    317   `j                 0    43954    sms_app_warehouse_goods_info 
   TABLE DATA           �  COPY public.sms_app_warehouse_goods_info (id, wh_job_no, wh_goods_invoice, wh_goods_pieces, wh_goods_length, wh_goods_width, wh_goods_height, wh_goods_weight, wh_goods_volume_weight, wh_uom, wh_chargeable_weight, "wh_CBM", wh_available_area, wh_available_volume, wh_goods_area, wh_customer_name, wh_customer_type, wh_bay_id, wh_branch_id, wh_check_in_out, wh_damages, wh_dimension_deviation, wh_goods_package_type_id, wh_goods_status, wh_mismatches, wh_no_of_units_deviation, wh_ratification_process, wh_unit_id, wh_weights_deviation, wh_stack_layer_id, wh_checkin_time, wh_qr_rand_num, wh_dispatch_num, wh_consignee, wh_consigner, wh_checkout_time, wh_storage_time) FROM stdin;
    public          postgres    false    325   }j                0    43945    sms_app_warehouse_stock_info 
   TABLE DATA           N  COPY public.sms_app_warehouse_stock_info (id, wh_stock_invoice, wh_stock_customer_name, wh_stock_arrival_date, wh_stock_unloading_start_time, wh_stock_unloading_end_time, "wh_stock_FRD_time", wh_stock_invoice_value, wh_stock_amount_in, wh_stock_transporters, wh_stock_truck_number, wh_stock_truck_type, wh_stock_consigner_name, wh_stock_consignee_name, wh_stock_docs_received, "wh_stock_HAWB", "wh_stock_MAWB", wh_stock_destination, wh_stock_case_number, wh_stock_invoice_weight, "wh_stock_CBM", wh_stock_eway_bill, wh_stock_fumigation_status, wh_stock_location, wh_stock_days_in_wh, wh_stock_ship_date, wh_stock_out_time, wh_stock_labels_pasted_by, wh_stock_remarks, wh_stock_driver_name, wh_stock_driver_contact, wh_stock_driver_lic, wh_stock_driver_name_out, wh_stock_driver_contact_out, wh_stock_driver_lic_out, wh_stock_arrival_date_out, wh_stock_unloading_start_time_out, wh_stock_unloading_end_time_out, "wh_stock_FRD_time_out", wh_stock_transporters_out, wh_stock_truck_number_out, wh_stock_truck_type_out, wh_stock_invoice_currency_id, wh_stock_movement_type_id, wh_stock_type_id) FROM stdin;
    public          postgres    false    323   tm                0    43938    sms_app_whratemasterinfo 
   TABLE DATA           Z  COPY public.sms_app_whratemasterinfo (id, whrm_customer_name, whrm_storage_charge, whrm_loading_charge, whrm_unloading_charge, whrm_forkliftloading_charge, whrm_forkliftunloading_charge, whrm_crane_loading_charge, whrm_crane_unloading_charge, whrm_over_time_charge, whrm_insurance_charge, whrm_addmanpow_charge, whrm_storage_type_id) FROM stdin;
    public          postgres    false    321   �m                0    43931    sms_app_whstoragetypeinfo 
   TABLE DATA           M   COPY public.sms_app_whstoragetypeinfo (id, "Whstoragetype_name") FROM stdin;
    public          postgres    false    319   �m      �           0    0    auth_group_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);
          public          postgres    false    215            �           0    0    auth_group_permissions_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);
          public          postgres    false    217            �           0    0    auth_permission_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.auth_permission_id_seq', 332, true);
          public          postgres    false    213            �           0    0    auth_user_groups_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);
          public          postgres    false    221            �           0    0    auth_user_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.auth_user_id_seq', 2, true);
          public          postgres    false    219            �           0    0 !   auth_user_user_permissions_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);
          public          postgres    false    223            �           0    0    django_admin_log_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.django_admin_log_id_seq', 40, true);
          public          postgres    false    225            �           0    0    django_content_type_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.django_content_type_id_seq', 83, true);
          public          postgres    false    211            �           0    0    django_migrations_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.django_migrations_id_seq', 111, true);
          public          postgres    false    209            �           0    0 !   sms_app_activeinactiveinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_activeinactiveinfo_id_seq', 2, true);
          public          postgres    false    372            �           0    0    sms_app_assetinfo_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.sms_app_assetinfo_id_seq', 1, false);
          public          postgres    false    228            �           0    0     sms_app_assign_asset_info_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_assign_asset_info_id_seq', 1, false);
          public          postgres    false    360            �           0    0    sms_app_axletypeinfo_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.sms_app_axletypeinfo_id_seq', 1, false);
          public          postgres    false    230            �           0    0    sms_app_bayinfo_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.sms_app_bayinfo_id_seq', 3, true);
          public          postgres    false    232            �           0    0    sms_app_bodyinfo_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.sms_app_bodyinfo_id_seq', 1, false);
          public          postgres    false    234            �           0    0    sms_app_check_in_out_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.sms_app_check_in_out_id_seq', 2, true);
          public          postgres    false    362            �           0    0    sms_app_city_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.sms_app_city_id_seq', 1, false);
          public          postgres    false    236            �           0    0 $   sms_app_consignmentdetailinfo_id_seq    SEQUENCE SET     S   SELECT pg_catalog.setval('public.sms_app_consignmentdetailinfo_id_seq', 1, false);
          public          postgres    false    358            �           0    0    sms_app_country_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.sms_app_country_id_seq', 2, true);
          public          postgres    false    238            �           0    0    sms_app_crcountfrominfo_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.sms_app_crcountfrominfo_id_seq', 1, false);
          public          postgres    false    240            �           0    0    sms_app_currency_type_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.sms_app_currency_type_id_seq', 1, false);
          public          postgres    false    242            �           0    0 %   sms_app_customerdepartmentinfo_id_seq    SEQUENCE SET     T   SELECT pg_catalog.setval('public.sms_app_customerdepartmentinfo_id_seq', 1, false);
          public          postgres    false    244            �           0    0    sms_app_customerinfo_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.sms_app_customerinfo_id_seq', 2, true);
          public          postgres    false    246            �           0    0 #   sms_app_customernameinfo_new_id_seq    SEQUENCE SET     R   SELECT pg_catalog.setval('public.sms_app_customernameinfo_new_id_seq', 1, false);
          public          postgres    false    248            �           0    0    sms_app_customertypeinfo_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.sms_app_customertypeinfo_id_seq', 2, true);
          public          postgres    false    250            �           0    0    sms_app_damageinfo_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.sms_app_damageinfo_id_seq', 1, false);
          public          postgres    false    252            �           0    0 !   sms_app_damagereportimages_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.sms_app_damagereportimages_id_seq', 30, true);
          public          postgres    false    370            �           0    0    sms_app_damagereportinfo_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.sms_app_damagereportinfo_id_seq', 38, true);
          public          postgres    false    356            �           0    0    sms_app_department_info_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.sms_app_department_info_id_seq', 6, true);
          public          postgres    false    254            �           0    0    sms_app_designationinfo_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.sms_app_designationinfo_id_seq', 1, false);
          public          postgres    false    256            �           0    0    sms_app_dispatch_info_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.sms_app_dispatch_info_id_seq', 4, true);
          public          postgres    false    376            �           0    0    sms_app_employee_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.sms_app_employee_id_seq', 1, false);
          public          postgres    false    354            �           0    0    sms_app_enquiry_info_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.sms_app_enquiry_info_id_seq', 1, false);
          public          postgres    false    258            �           0    0    sms_app_enquirynoteinfo_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.sms_app_enquirynoteinfo_id_seq', 1, false);
          public          postgres    false    352            �           0    0    sms_app_fueltypeinfo_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.sms_app_fueltypeinfo_id_seq', 1, false);
          public          postgres    false    260            �           0    0    sms_app_gatein_info_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.sms_app_gatein_info_id_seq', 19, true);
          public          postgres    false    350            �           0    0     sms_app_gstexcemptioninfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_gstexcemptioninfo_id_seq', 1, false);
          public          postgres    false    262            �           0    0    sms_app_gstmodelinfo_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.sms_app_gstmodelinfo_id_seq', 1, false);
          public          postgres    false    264            �           0    0    sms_app_insurance_info_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.sms_app_insurance_info_id_seq', 1, false);
          public          postgres    false    348            �           0    0    sms_app_insurance_type_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.sms_app_insurance_type_id_seq', 1, false);
          public          postgres    false    266            �           0    0    sms_app_loadingbay_info_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.sms_app_loadingbay_info_id_seq', 41, true);
          public          postgres    false    346            �           0    0 $   sms_app_loadingbayimages_info_id_seq    SEQUENCE SET     R   SELECT pg_catalog.setval('public.sms_app_loadingbayimages_info_id_seq', 5, true);
          public          postgres    false    378            �           0    0    sms_app_location_info_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.sms_app_location_info_id_seq', 1, false);
          public          postgres    false    268            �           0    0 !   sms_app_locationmasterinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_locationmasterinfo_id_seq', 8, true);
          public          postgres    false    344            �           0    0 $   sms_app_materialhandling_info_id_seq    SEQUENCE SET     S   SELECT pg_catalog.setval('public.sms_app_materialhandling_info_id_seq', 1, false);
          public          postgres    false    270            �           0    0    sms_app_movementtypeinfo_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.sms_app_movementtypeinfo_id_seq', 1, false);
          public          postgres    false    272            �           0    0    sms_app_ownershipinfo_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.sms_app_ownershipinfo_id_seq', 1, false);
          public          postgres    false    274            �           0    0    sms_app_packagetype_info_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.sms_app_packagetype_info_id_seq', 1, false);
          public          postgres    false    276            �           0    0    sms_app_paymenttypeinfo_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.sms_app_paymenttypeinfo_id_seq', 1, false);
          public          postgres    false    278            �           0    0    sms_app_peo_reg_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.sms_app_peo_reg_id_seq', 1, false);
          public          postgres    false    280            �           0    0    sms_app_permittypeinfo_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.sms_app_permittypeinfo_id_seq', 1, false);
          public          postgres    false    282            �           0    0    sms_app_prod_cat_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.sms_app_prod_cat_id_seq', 1, false);
          public          postgres    false    284            �           0    0    sms_app_prod_type_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.sms_app_prod_type_id_seq', 1, false);
          public          postgres    false    286            �           0    0    sms_app_product_info_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.sms_app_product_info_id_seq', 1, false);
          public          postgres    false    342            �           0    0    sms_app_received_not_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.sms_app_received_not_id_seq', 2, true);
          public          postgres    false    366            �           0    0    sms_app_roleinfo_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.sms_app_roleinfo_id_seq', 1, false);
          public          postgres    false    288            �           0    0    sms_app_rtratemasterinfo_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.sms_app_rtratemasterinfo_id_seq', 1, false);
          public          postgres    false    340            �           0    0    sms_app_service_info_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.sms_app_service_info_id_seq', 1, false);
          public          postgres    false    338            �           0    0    sms_app_stackinginfo_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.sms_app_stackinginfo_id_seq', 5, true);
          public          postgres    false    374            �           0    0    sms_app_state_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.sms_app_state_id_seq', 1, false);
          public          postgres    false    290            �           0    0    sms_app_statuslist_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.sms_app_statuslist_id_seq', 13, true);
          public          postgres    false    292            �           0    0 "   sms_app_stock_movement_type_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.sms_app_stock_movement_type_id_seq', 1, false);
          public          postgres    false    294            �           0    0    sms_app_stock_type_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.sms_app_stock_type_id_seq', 1, false);
          public          postgres    false    296            �           0    0    sms_app_stud_reg_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.sms_app_stud_reg_id_seq', 1, false);
          public          postgres    false    298            �           0    0 !   sms_app_trbusinesstypeinfo_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.sms_app_trbusinesstypeinfo_id_seq', 1, false);
          public          postgres    false    300            �           0    0    sms_app_tripclosureinfo_id_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.sms_app_tripclosureinfo_id_seq', 1, false);
          public          postgres    false    336            �           0    0    sms_app_tripdetailinfo_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.sms_app_tripdetailinfo_id_seq', 1, false);
          public          postgres    false    334            �           0    0    sms_app_unitinfo_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.sms_app_unitinfo_id_seq', 3, true);
          public          postgres    false    302            �           0    0    sms_app_uom_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.sms_app_uom_id_seq', 2, true);
          public          postgres    false    364            �           0    0    sms_app_uploadinfo_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.sms_app_uploadinfo_id_seq', 7, true);
          public          postgres    false    368            �           0    0    sms_app_user_extinfo_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.sms_app_user_extinfo_id_seq', 1, true);
          public          postgres    false    332            �           0    0 "   sms_app_vehiclecategoryinfo_id_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.sms_app_vehiclecategoryinfo_id_seq', 1, false);
          public          postgres    false    304            �           0    0     sms_app_vehiclecolourinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_vehiclecolourinfo_id_seq', 1, false);
          public          postgres    false    306            �           0    0     sms_app_vehicledetailinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_vehicledetailinfo_id_seq', 1, false);
          public          postgres    false    330            �           0    0     sms_app_vehiclemasterinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_vehiclemasterinfo_id_seq', 1, false);
          public          postgres    false    328            �           0    0    sms_app_vehiclemodelinfo_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.sms_app_vehiclemodelinfo_id_seq', 1, false);
          public          postgres    false    308            �           0    0     sms_app_vehiclenumberinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_vehiclenumberinfo_id_seq', 1, false);
          public          postgres    false    310            �           0    0     sms_app_vehiclesourceinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_vehiclesourceinfo_id_seq', 1, false);
          public          postgres    false    312                        0    0    sms_app_vehicletypeinfo_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.sms_app_vehicletypeinfo_id_seq', 4, true);
          public          postgres    false    314                       0    0    sms_app_vendor_info_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.sms_app_vendor_info_id_seq', 1, false);
          public          postgres    false    326                       0    0 !   sms_app_vhmanufacturerinfo_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.sms_app_vhmanufacturerinfo_id_seq', 1, false);
          public          postgres    false    316                       0    0 #   sms_app_warehouse_goods_info_id_seq    SEQUENCE SET     R   SELECT pg_catalog.setval('public.sms_app_warehouse_goods_info_id_seq', 20, true);
          public          postgres    false    324                       0    0 #   sms_app_warehouse_stock_info_id_seq    SEQUENCE SET     R   SELECT pg_catalog.setval('public.sms_app_warehouse_stock_info_id_seq', 1, false);
          public          postgres    false    322                       0    0    sms_app_whratemasterinfo_id_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public.sms_app_whratemasterinfo_id_seq', 1, false);
          public          postgres    false    320                       0    0     sms_app_whstoragetypeinfo_id_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.sms_app_whstoragetypeinfo_id_seq', 1, false);
          public          postgres    false    318            g           2606    43604    auth_group auth_group_name_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);
 H   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_name_key;
       public            postgres    false    216            l           2606    43534 R   auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);
 |   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
       public            postgres    false    218    218            o           2606    43500 2   auth_group_permissions auth_group_permissions_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_pkey;
       public            postgres    false    218            i           2606    43491    auth_group auth_group_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_pkey;
       public            postgres    false    216            b           2606    43525 F   auth_permission auth_permission_content_type_id_codename_01ab375a_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);
 p   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq;
       public            postgres    false    214    214            d           2606    43484 $   auth_permission auth_permission_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_pkey;
       public            postgres    false    214            w           2606    43516 &   auth_user_groups auth_user_groups_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_pkey;
       public            postgres    false    222            z           2606    43549 @   auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);
 j   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq;
       public            postgres    false    222    222            q           2606    43507    auth_user auth_user_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_pkey;
       public            postgres    false    220            }           2606    43523 :   auth_user_user_permissions auth_user_user_permissions_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_pkey;
       public            postgres    false    224            �           2606    43563 Y   auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);
 �   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq;
       public            postgres    false    224    224            t           2606    43599     auth_user auth_user_username_key 
   CONSTRAINT     _   ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);
 J   ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_username_key;
       public            postgres    false    220            �           2606    43585 &   django_admin_log django_admin_log_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
       public            postgres    false    226            ]           2606    43477 E   django_content_type django_content_type_app_label_model_76bd3d3b_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);
 o   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq;
       public            postgres    false    212    212            _           2606    43475 ,   django_content_type django_content_type_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
       public            postgres    false    212            [           2606    43468 (   django_migrations django_migrations_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.django_migrations DROP CONSTRAINT django_migrations_pkey;
       public            postgres    false    210            �           2606    43612 "   django_session django_session_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
 L   ALTER TABLE ONLY public.django_session DROP CONSTRAINT django_session_pkey;
       public            postgres    false    227            �           2606    45144 :   sms_app_activeinactiveinfo sms_app_activeinactiveinfo_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.sms_app_activeinactiveinfo
    ADD CONSTRAINT sms_app_activeinactiveinfo_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.sms_app_activeinactiveinfo DROP CONSTRAINT sms_app_activeinactiveinfo_pkey;
       public            postgres    false    373            �           2606    43621 (   sms_app_assetinfo sms_app_assetinfo_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.sms_app_assetinfo
    ADD CONSTRAINT sms_app_assetinfo_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.sms_app_assetinfo DROP CONSTRAINT sms_app_assetinfo_pkey;
       public            postgres    false    229            �           2606    44163 8   sms_app_assign_asset_info sms_app_assign_asset_info_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_assign_asset_info
    ADD CONSTRAINT sms_app_assign_asset_info_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_assign_asset_info DROP CONSTRAINT sms_app_assign_asset_info_pkey;
       public            postgres    false    361            �           2606    43628 .   sms_app_axletypeinfo sms_app_axletypeinfo_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_axletypeinfo
    ADD CONSTRAINT sms_app_axletypeinfo_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_axletypeinfo DROP CONSTRAINT sms_app_axletypeinfo_pkey;
       public            postgres    false    231            �           2606    43635 $   sms_app_bayinfo sms_app_bayinfo_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.sms_app_bayinfo
    ADD CONSTRAINT sms_app_bayinfo_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.sms_app_bayinfo DROP CONSTRAINT sms_app_bayinfo_pkey;
       public            postgres    false    233            �           2606    43642 &   sms_app_bodyinfo sms_app_bodyinfo_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.sms_app_bodyinfo
    ADD CONSTRAINT sms_app_bodyinfo_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.sms_app_bodyinfo DROP CONSTRAINT sms_app_bodyinfo_pkey;
       public            postgres    false    235            �           2606    44890 .   sms_app_check_in_out sms_app_check_in_out_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_check_in_out
    ADD CONSTRAINT sms_app_check_in_out_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_check_in_out DROP CONSTRAINT sms_app_check_in_out_pkey;
       public            postgres    false    363            �           2606    43649    sms_app_city sms_app_city_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.sms_app_city
    ADD CONSTRAINT sms_app_city_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.sms_app_city DROP CONSTRAINT sms_app_city_pkey;
       public            postgres    false    237            �           2606    44136 @   sms_app_consignmentdetailinfo sms_app_consignmentdetailinfo_pkey 
   CONSTRAINT     ~   ALTER TABLE ONLY public.sms_app_consignmentdetailinfo
    ADD CONSTRAINT sms_app_consignmentdetailinfo_pkey PRIMARY KEY (id);
 j   ALTER TABLE ONLY public.sms_app_consignmentdetailinfo DROP CONSTRAINT sms_app_consignmentdetailinfo_pkey;
       public            postgres    false    359            �           2606    43656 $   sms_app_country sms_app_country_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.sms_app_country
    ADD CONSTRAINT sms_app_country_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.sms_app_country DROP CONSTRAINT sms_app_country_pkey;
       public            postgres    false    239            �           2606    43663 4   sms_app_crcountfrominfo sms_app_crcountfrominfo_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_crcountfrominfo
    ADD CONSTRAINT sms_app_crcountfrominfo_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_crcountfrominfo DROP CONSTRAINT sms_app_crcountfrominfo_pkey;
       public            postgres    false    241            �           2606    43670 0   sms_app_currency_type sms_app_currency_type_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.sms_app_currency_type
    ADD CONSTRAINT sms_app_currency_type_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.sms_app_currency_type DROP CONSTRAINT sms_app_currency_type_pkey;
       public            postgres    false    243            �           2606    43677 B   sms_app_customerdepartmentinfo sms_app_customerdepartmentinfo_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerdepartmentinfo
    ADD CONSTRAINT sms_app_customerdepartmentinfo_pkey PRIMARY KEY (id);
 l   ALTER TABLE ONLY public.sms_app_customerdepartmentinfo DROP CONSTRAINT sms_app_customerdepartmentinfo_pkey;
       public            postgres    false    245            �           2606    43684 .   sms_app_customerinfo sms_app_customerinfo_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_pkey;
       public            postgres    false    247            �           2606    43691 >   sms_app_customernameinfo_new sms_app_customernameinfo_new_pkey 
   CONSTRAINT     |   ALTER TABLE ONLY public.sms_app_customernameinfo_new
    ADD CONSTRAINT sms_app_customernameinfo_new_pkey PRIMARY KEY (id);
 h   ALTER TABLE ONLY public.sms_app_customernameinfo_new DROP CONSTRAINT sms_app_customernameinfo_new_pkey;
       public            postgres    false    249            �           2606    43698 6   sms_app_customertypeinfo sms_app_customertypeinfo_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.sms_app_customertypeinfo
    ADD CONSTRAINT sms_app_customertypeinfo_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.sms_app_customertypeinfo DROP CONSTRAINT sms_app_customertypeinfo_pkey;
       public            postgres    false    251            �           2606    43705 *   sms_app_damageinfo sms_app_damageinfo_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.sms_app_damageinfo
    ADD CONSTRAINT sms_app_damageinfo_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.sms_app_damageinfo DROP CONSTRAINT sms_app_damageinfo_pkey;
       public            postgres    false    253            �           2606    45113 :   sms_app_damagereportimages sms_app_damagereportimages_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.sms_app_damagereportimages
    ADD CONSTRAINT sms_app_damagereportimages_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.sms_app_damagereportimages DROP CONSTRAINT sms_app_damagereportimages_pkey;
       public            postgres    false    371                       2606    44094 6   sms_app_damagereportinfo sms_app_damagereportinfo_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.sms_app_damagereportinfo
    ADD CONSTRAINT sms_app_damagereportinfo_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.sms_app_damagereportinfo DROP CONSTRAINT sms_app_damagereportinfo_pkey;
       public            postgres    false    357            �           2606    43712 4   sms_app_department_info sms_app_department_info_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_department_info
    ADD CONSTRAINT sms_app_department_info_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_department_info DROP CONSTRAINT sms_app_department_info_pkey;
       public            postgres    false    255            �           2606    43719 4   sms_app_designationinfo sms_app_designationinfo_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_designationinfo
    ADD CONSTRAINT sms_app_designationinfo_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_designationinfo DROP CONSTRAINT sms_app_designationinfo_pkey;
       public            postgres    false    257            �           2606    45209 0   sms_app_dispatch_info sms_app_dispatch_info_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.sms_app_dispatch_info
    ADD CONSTRAINT sms_app_dispatch_info_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.sms_app_dispatch_info DROP CONSTRAINT sms_app_dispatch_info_pkey;
       public            postgres    false    377            {           2606    44082 &   sms_app_employee sms_app_employee_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.sms_app_employee
    ADD CONSTRAINT sms_app_employee_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.sms_app_employee DROP CONSTRAINT sms_app_employee_pkey;
       public            postgres    false    355            �           2606    43726 .   sms_app_enquiry_info sms_app_enquiry_info_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_enquiry_info
    ADD CONSTRAINT sms_app_enquiry_info_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_enquiry_info DROP CONSTRAINT sms_app_enquiry_info_pkey;
       public            postgres    false    259            x           2606    44073 4   sms_app_enquirynoteinfo sms_app_enquirynoteinfo_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynoteinfo_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynoteinfo_pkey;
       public            postgres    false    353            �           2606    43733 .   sms_app_fueltypeinfo sms_app_fueltypeinfo_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_fueltypeinfo
    ADD CONSTRAINT sms_app_fueltypeinfo_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_fueltypeinfo DROP CONSTRAINT sms_app_fueltypeinfo_pkey;
       public            postgres    false    261            n           2606    44066 ,   sms_app_gatein_info sms_app_gatein_info_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.sms_app_gatein_info
    ADD CONSTRAINT sms_app_gatein_info_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.sms_app_gatein_info DROP CONSTRAINT sms_app_gatein_info_pkey;
       public            postgres    false    351            �           2606    43740 8   sms_app_gstexcemptioninfo sms_app_gstexcemptioninfo_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_gstexcemptioninfo
    ADD CONSTRAINT sms_app_gstexcemptioninfo_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_gstexcemptioninfo DROP CONSTRAINT sms_app_gstexcemptioninfo_pkey;
       public            postgres    false    263            �           2606    43747 .   sms_app_gstmodelinfo sms_app_gstmodelinfo_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_gstmodelinfo
    ADD CONSTRAINT sms_app_gstmodelinfo_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_gstmodelinfo DROP CONSTRAINT sms_app_gstmodelinfo_pkey;
       public            postgres    false    265            g           2606    44059 2   sms_app_insurance_info sms_app_insurance_info_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.sms_app_insurance_info
    ADD CONSTRAINT sms_app_insurance_info_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.sms_app_insurance_info DROP CONSTRAINT sms_app_insurance_info_pkey;
       public            postgres    false    349            �           2606    43754 2   sms_app_insurance_type sms_app_insurance_type_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.sms_app_insurance_type
    ADD CONSTRAINT sms_app_insurance_type_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.sms_app_insurance_type DROP CONSTRAINT sms_app_insurance_type_pkey;
       public            postgres    false    267            b           2606    44052 4   sms_app_loadingbay_info sms_app_loadingbay_info_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_loadingbay_info
    ADD CONSTRAINT sms_app_loadingbay_info_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_loadingbay_info DROP CONSTRAINT sms_app_loadingbay_info_pkey;
       public            postgres    false    347            �           2606    45305 @   sms_app_loadingbayimages_info sms_app_loadingbayimages_info_pkey 
   CONSTRAINT     ~   ALTER TABLE ONLY public.sms_app_loadingbayimages_info
    ADD CONSTRAINT sms_app_loadingbayimages_info_pkey PRIMARY KEY (id);
 j   ALTER TABLE ONLY public.sms_app_loadingbayimages_info DROP CONSTRAINT sms_app_loadingbayimages_info_pkey;
       public            postgres    false    379            �           2606    43761 0   sms_app_location_info sms_app_location_info_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.sms_app_location_info
    ADD CONSTRAINT sms_app_location_info_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.sms_app_location_info DROP CONSTRAINT sms_app_location_info_pkey;
       public            postgres    false    269            Z           2606    44035 :   sms_app_locationmasterinfo sms_app_locationmasterinfo_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.sms_app_locationmasterinfo
    ADD CONSTRAINT sms_app_locationmasterinfo_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.sms_app_locationmasterinfo DROP CONSTRAINT sms_app_locationmasterinfo_pkey;
       public            postgres    false    345            �           2606    43768 @   sms_app_materialhandling_info sms_app_materialhandling_info_pkey 
   CONSTRAINT     ~   ALTER TABLE ONLY public.sms_app_materialhandling_info
    ADD CONSTRAINT sms_app_materialhandling_info_pkey PRIMARY KEY (id);
 j   ALTER TABLE ONLY public.sms_app_materialhandling_info DROP CONSTRAINT sms_app_materialhandling_info_pkey;
       public            postgres    false    271            �           2606    43775 6   sms_app_movementtypeinfo sms_app_movementtypeinfo_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.sms_app_movementtypeinfo
    ADD CONSTRAINT sms_app_movementtypeinfo_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.sms_app_movementtypeinfo DROP CONSTRAINT sms_app_movementtypeinfo_pkey;
       public            postgres    false    273            �           2606    43782 0   sms_app_ownershipinfo sms_app_ownershipinfo_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.sms_app_ownershipinfo
    ADD CONSTRAINT sms_app_ownershipinfo_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.sms_app_ownershipinfo DROP CONSTRAINT sms_app_ownershipinfo_pkey;
       public            postgres    false    275            �           2606    43789 6   sms_app_packagetype_info sms_app_packagetype_info_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.sms_app_packagetype_info
    ADD CONSTRAINT sms_app_packagetype_info_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.sms_app_packagetype_info DROP CONSTRAINT sms_app_packagetype_info_pkey;
       public            postgres    false    277            �           2606    43796 4   sms_app_paymenttypeinfo sms_app_paymenttypeinfo_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_paymenttypeinfo
    ADD CONSTRAINT sms_app_paymenttypeinfo_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_paymenttypeinfo DROP CONSTRAINT sms_app_paymenttypeinfo_pkey;
       public            postgres    false    279            �           2606    43803 $   sms_app_peo_reg sms_app_peo_reg_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.sms_app_peo_reg
    ADD CONSTRAINT sms_app_peo_reg_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.sms_app_peo_reg DROP CONSTRAINT sms_app_peo_reg_pkey;
       public            postgres    false    281            �           2606    43810 2   sms_app_permittypeinfo sms_app_permittypeinfo_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.sms_app_permittypeinfo
    ADD CONSTRAINT sms_app_permittypeinfo_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.sms_app_permittypeinfo DROP CONSTRAINT sms_app_permittypeinfo_pkey;
       public            postgres    false    283            �           2606    43817 &   sms_app_prod_cat sms_app_prod_cat_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.sms_app_prod_cat
    ADD CONSTRAINT sms_app_prod_cat_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.sms_app_prod_cat DROP CONSTRAINT sms_app_prod_cat_pkey;
       public            postgres    false    285            �           2606    43824 (   sms_app_prod_type sms_app_prod_type_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.sms_app_prod_type
    ADD CONSTRAINT sms_app_prod_type_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.sms_app_prod_type DROP CONSTRAINT sms_app_prod_type_pkey;
       public            postgres    false    287            R           2606    44028 .   sms_app_product_info sms_app_product_info_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_product_info
    ADD CONSTRAINT sms_app_product_info_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_product_info DROP CONSTRAINT sms_app_product_info_pkey;
       public            postgres    false    343            �           2606    45050 .   sms_app_received_not sms_app_received_not_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_received_not
    ADD CONSTRAINT sms_app_received_not_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_received_not DROP CONSTRAINT sms_app_received_not_pkey;
       public            postgres    false    367            �           2606    43831 &   sms_app_roleinfo sms_app_roleinfo_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.sms_app_roleinfo
    ADD CONSTRAINT sms_app_roleinfo_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.sms_app_roleinfo DROP CONSTRAINT sms_app_roleinfo_pkey;
       public            postgres    false    289            K           2606    44021 6   sms_app_rtratemasterinfo sms_app_rtratemasterinfo_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.sms_app_rtratemasterinfo
    ADD CONSTRAINT sms_app_rtratemasterinfo_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.sms_app_rtratemasterinfo DROP CONSTRAINT sms_app_rtratemasterinfo_pkey;
       public            postgres    false    341            F           2606    44014 .   sms_app_service_info sms_app_service_info_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_service_info
    ADD CONSTRAINT sms_app_service_info_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_service_info DROP CONSTRAINT sms_app_service_info_pkey;
       public            postgres    false    339            �           2606    45196 .   sms_app_stackinginfo sms_app_stackinginfo_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_stackinginfo
    ADD CONSTRAINT sms_app_stackinginfo_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_stackinginfo DROP CONSTRAINT sms_app_stackinginfo_pkey;
       public            postgres    false    375            �           2606    43838     sms_app_state sms_app_state_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.sms_app_state
    ADD CONSTRAINT sms_app_state_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.sms_app_state DROP CONSTRAINT sms_app_state_pkey;
       public            postgres    false    291            �           2606    43845 *   sms_app_statuslist sms_app_statuslist_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.sms_app_statuslist
    ADD CONSTRAINT sms_app_statuslist_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.sms_app_statuslist DROP CONSTRAINT sms_app_statuslist_pkey;
       public            postgres    false    293            �           2606    43852 <   sms_app_stock_movement_type sms_app_stock_movement_type_pkey 
   CONSTRAINT     z   ALTER TABLE ONLY public.sms_app_stock_movement_type
    ADD CONSTRAINT sms_app_stock_movement_type_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.sms_app_stock_movement_type DROP CONSTRAINT sms_app_stock_movement_type_pkey;
       public            postgres    false    295            �           2606    43859 *   sms_app_stock_type sms_app_stock_type_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.sms_app_stock_type
    ADD CONSTRAINT sms_app_stock_type_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.sms_app_stock_type DROP CONSTRAINT sms_app_stock_type_pkey;
       public            postgres    false    297            �           2606    43866 &   sms_app_stud_reg sms_app_stud_reg_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.sms_app_stud_reg
    ADD CONSTRAINT sms_app_stud_reg_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.sms_app_stud_reg DROP CONSTRAINT sms_app_stud_reg_pkey;
       public            postgres    false    299            �           2606    43873 :   sms_app_trbusinesstypeinfo sms_app_trbusinesstypeinfo_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.sms_app_trbusinesstypeinfo
    ADD CONSTRAINT sms_app_trbusinesstypeinfo_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.sms_app_trbusinesstypeinfo DROP CONSTRAINT sms_app_trbusinesstypeinfo_pkey;
       public            postgres    false    301            C           2606    44007 4   sms_app_tripclosureinfo sms_app_tripclosureinfo_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_tripclosureinfo
    ADD CONSTRAINT sms_app_tripclosureinfo_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_tripclosureinfo DROP CONSTRAINT sms_app_tripclosureinfo_pkey;
       public            postgres    false    337            =           2606    44000 2   sms_app_tripdetailinfo sms_app_tripdetailinfo_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.sms_app_tripdetailinfo
    ADD CONSTRAINT sms_app_tripdetailinfo_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.sms_app_tripdetailinfo DROP CONSTRAINT sms_app_tripdetailinfo_pkey;
       public            postgres    false    335            �           2606    43880 &   sms_app_unitinfo sms_app_unitinfo_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.sms_app_unitinfo
    ADD CONSTRAINT sms_app_unitinfo_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.sms_app_unitinfo DROP CONSTRAINT sms_app_unitinfo_pkey;
       public            postgres    false    303            �           2606    44914    sms_app_uom sms_app_uom_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.sms_app_uom
    ADD CONSTRAINT sms_app_uom_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.sms_app_uom DROP CONSTRAINT sms_app_uom_pkey;
       public            postgres    false    365            �           2606    45067 *   sms_app_uploadinfo sms_app_uploadinfo_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.sms_app_uploadinfo
    ADD CONSTRAINT sms_app_uploadinfo_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.sms_app_uploadinfo DROP CONSTRAINT sms_app_uploadinfo_pkey;
       public            postgres    false    369            9           2606    43991 .   sms_app_user_extinfo sms_app_user_extinfo_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.sms_app_user_extinfo
    ADD CONSTRAINT sms_app_user_extinfo_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.sms_app_user_extinfo DROP CONSTRAINT sms_app_user_extinfo_pkey;
       public            postgres    false    333            ;           2606    43993 5   sms_app_user_extinfo sms_app_user_extinfo_user_id_key 
   CONSTRAINT     s   ALTER TABLE ONLY public.sms_app_user_extinfo
    ADD CONSTRAINT sms_app_user_extinfo_user_id_key UNIQUE (user_id);
 _   ALTER TABLE ONLY public.sms_app_user_extinfo DROP CONSTRAINT sms_app_user_extinfo_user_id_key;
       public            postgres    false    333            �           2606    43887 <   sms_app_vehiclecategoryinfo sms_app_vehiclecategoryinfo_pkey 
   CONSTRAINT     z   ALTER TABLE ONLY public.sms_app_vehiclecategoryinfo
    ADD CONSTRAINT sms_app_vehiclecategoryinfo_pkey PRIMARY KEY (id);
 f   ALTER TABLE ONLY public.sms_app_vehiclecategoryinfo DROP CONSTRAINT sms_app_vehiclecategoryinfo_pkey;
       public            postgres    false    305            �           2606    43894 8   sms_app_vehiclecolourinfo sms_app_vehiclecolourinfo_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_vehiclecolourinfo
    ADD CONSTRAINT sms_app_vehiclecolourinfo_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_vehiclecolourinfo DROP CONSTRAINT sms_app_vehiclecolourinfo_pkey;
       public            postgres    false    307            .           2606    43984 8   sms_app_vehicledetailinfo sms_app_vehicledetailinfo_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_vehicledetailinfo
    ADD CONSTRAINT sms_app_vehicledetailinfo_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_vehicledetailinfo DROP CONSTRAINT sms_app_vehicledetailinfo_pkey;
       public            postgres    false    331                       2606    43977 8   sms_app_vehiclemasterinfo sms_app_vehiclemasterinfo_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemasterinfo_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemasterinfo_pkey;
       public            postgres    false    329            �           2606    43901 6   sms_app_vehiclemodelinfo sms_app_vehiclemodelinfo_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.sms_app_vehiclemodelinfo
    ADD CONSTRAINT sms_app_vehiclemodelinfo_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.sms_app_vehiclemodelinfo DROP CONSTRAINT sms_app_vehiclemodelinfo_pkey;
       public            postgres    false    309            �           2606    43908 8   sms_app_vehiclenumberinfo sms_app_vehiclenumberinfo_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_vehiclenumberinfo
    ADD CONSTRAINT sms_app_vehiclenumberinfo_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_vehiclenumberinfo DROP CONSTRAINT sms_app_vehiclenumberinfo_pkey;
       public            postgres    false    311            �           2606    43915 8   sms_app_vehiclesourceinfo sms_app_vehiclesourceinfo_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_vehiclesourceinfo
    ADD CONSTRAINT sms_app_vehiclesourceinfo_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_vehiclesourceinfo DROP CONSTRAINT sms_app_vehiclesourceinfo_pkey;
       public            postgres    false    313            �           2606    43922 4   sms_app_vehicletypeinfo sms_app_vehicletypeinfo_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.sms_app_vehicletypeinfo
    ADD CONSTRAINT sms_app_vehicletypeinfo_pkey PRIMARY KEY (id);
 ^   ALTER TABLE ONLY public.sms_app_vehicletypeinfo DROP CONSTRAINT sms_app_vehicletypeinfo_pkey;
       public            postgres    false    315                       2606    43968 ,   sms_app_vendor_info sms_app_vendor_info_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.sms_app_vendor_info
    ADD CONSTRAINT sms_app_vendor_info_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.sms_app_vendor_info DROP CONSTRAINT sms_app_vendor_info_pkey;
       public            postgres    false    327            �           2606    43929 :   sms_app_vhmanufacturerinfo sms_app_vhmanufacturerinfo_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.sms_app_vhmanufacturerinfo
    ADD CONSTRAINT sms_app_vhmanufacturerinfo_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.sms_app_vhmanufacturerinfo DROP CONSTRAINT sms_app_vhmanufacturerinfo_pkey;
       public            postgres    false    317                       2606    43959 >   sms_app_warehouse_goods_info sms_app_warehouse_goods_info_pkey 
   CONSTRAINT     |   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_goods_info_pkey PRIMARY KEY (id);
 h   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_goods_info_pkey;
       public            postgres    false    325                       2606    43952 >   sms_app_warehouse_stock_info sms_app_warehouse_stock_info_pkey 
   CONSTRAINT     |   ALTER TABLE ONLY public.sms_app_warehouse_stock_info
    ADD CONSTRAINT sms_app_warehouse_stock_info_pkey PRIMARY KEY (id);
 h   ALTER TABLE ONLY public.sms_app_warehouse_stock_info DROP CONSTRAINT sms_app_warehouse_stock_info_pkey;
       public            postgres    false    323            �           2606    43943 6   sms_app_whratemasterinfo sms_app_whratemasterinfo_pkey 
   CONSTRAINT     t   ALTER TABLE ONLY public.sms_app_whratemasterinfo
    ADD CONSTRAINT sms_app_whratemasterinfo_pkey PRIMARY KEY (id);
 `   ALTER TABLE ONLY public.sms_app_whratemasterinfo DROP CONSTRAINT sms_app_whratemasterinfo_pkey;
       public            postgres    false    321            �           2606    43936 8   sms_app_whstoragetypeinfo sms_app_whstoragetypeinfo_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.sms_app_whstoragetypeinfo
    ADD CONSTRAINT sms_app_whstoragetypeinfo_pkey PRIMARY KEY (id);
 b   ALTER TABLE ONLY public.sms_app_whstoragetypeinfo DROP CONSTRAINT sms_app_whstoragetypeinfo_pkey;
       public            postgres    false    319            e           1259    43605    auth_group_name_a6ea08ec_like    INDEX     h   CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);
 1   DROP INDEX public.auth_group_name_a6ea08ec_like;
       public            postgres    false    216            j           1259    43545 (   auth_group_permissions_group_id_b120cbf9    INDEX     o   CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);
 <   DROP INDEX public.auth_group_permissions_group_id_b120cbf9;
       public            postgres    false    218            m           1259    43546 -   auth_group_permissions_permission_id_84c5c92e    INDEX     y   CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);
 A   DROP INDEX public.auth_group_permissions_permission_id_84c5c92e;
       public            postgres    false    218            `           1259    43531 (   auth_permission_content_type_id_2f476e4b    INDEX     o   CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);
 <   DROP INDEX public.auth_permission_content_type_id_2f476e4b;
       public            postgres    false    214            u           1259    43561 "   auth_user_groups_group_id_97559544    INDEX     c   CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);
 6   DROP INDEX public.auth_user_groups_group_id_97559544;
       public            postgres    false    222            x           1259    43560 !   auth_user_groups_user_id_6a12ed8b    INDEX     a   CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);
 5   DROP INDEX public.auth_user_groups_user_id_6a12ed8b;
       public            postgres    false    222            {           1259    43575 1   auth_user_user_permissions_permission_id_1fbb5f2c    INDEX     �   CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);
 E   DROP INDEX public.auth_user_user_permissions_permission_id_1fbb5f2c;
       public            postgres    false    224            ~           1259    43574 +   auth_user_user_permissions_user_id_a95ead1b    INDEX     u   CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);
 ?   DROP INDEX public.auth_user_user_permissions_user_id_a95ead1b;
       public            postgres    false    224            r           1259    43600     auth_user_username_6821ab7c_like    INDEX     n   CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);
 4   DROP INDEX public.auth_user_username_6821ab7c_like;
       public            postgres    false    220            �           1259    43596 )   django_admin_log_content_type_id_c4bce8eb    INDEX     q   CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);
 =   DROP INDEX public.django_admin_log_content_type_id_c4bce8eb;
       public            postgres    false    226            �           1259    43597 !   django_admin_log_user_id_c564eba6    INDEX     a   CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);
 5   DROP INDEX public.django_admin_log_user_id_c564eba6;
       public            postgres    false    226            �           1259    43614 #   django_session_expire_date_a5c62663    INDEX     e   CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);
 7   DROP INDEX public.django_session_expire_date_a5c62663;
       public            postgres    false    227            �           1259    43613 (   django_session_session_key_c0390e0f_like    INDEX     ~   CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);
 <   DROP INDEX public.django_session_session_key_c0390e0f_like;
       public            postgres    false    227            �           1259    44777 .   sms_app_assetinfo_asset_assignedto_id_f44be589    INDEX     {   CREATE INDEX sms_app_assetinfo_asset_assignedto_id_f44be589 ON public.sms_app_assetinfo USING btree (asset_assignedto_id);
 B   DROP INDEX public.sms_app_assetinfo_asset_assignedto_id_f44be589;
       public            postgres    false    229            �           1259    44778 5   sms_app_assetinfo_asset_insurance_details_id_ca581a27    INDEX     �   CREATE INDEX sms_app_assetinfo_asset_insurance_details_id_ca581a27 ON public.sms_app_assetinfo USING btree (asset_insurance_details_id);
 I   DROP INDEX public.sms_app_assetinfo_asset_insurance_details_id_ca581a27;
       public            postgres    false    229            �           1259    44779 ,   sms_app_assetinfo_asset_location_id_8a72cb33    INDEX     w   CREATE INDEX sms_app_assetinfo_asset_location_id_8a72cb33 ON public.sms_app_assetinfo USING btree (asset_location_id);
 @   DROP INDEX public.sms_app_assetinfo_asset_location_id_8a72cb33;
       public            postgres    false    229            �           1259    44780 +   sms_app_assetinfo_asset_product_id_4a65faf4    INDEX     u   CREATE INDEX sms_app_assetinfo_asset_product_id_4a65faf4 ON public.sms_app_assetinfo USING btree (asset_product_id);
 ?   DROP INDEX public.sms_app_assetinfo_asset_product_id_4a65faf4;
       public            postgres    false    229            �           1259    44781 (   sms_app_assetinfo_asset_unit_id_3ce46701    INDEX     o   CREATE INDEX sms_app_assetinfo_asset_unit_id_3ce46701 ON public.sms_app_assetinfo USING btree (asset_unit_id);
 <   DROP INDEX public.sms_app_assetinfo_asset_unit_id_3ce46701;
       public            postgres    false    229            �           1259    44782 *   sms_app_assetinfo_asset_vendor_id_f06cbf62    INDEX     s   CREATE INDEX sms_app_assetinfo_asset_vendor_id_f06cbf62 ON public.sms_app_assetinfo USING btree (asset_vendor_id);
 >   DROP INDEX public.sms_app_assetinfo_asset_vendor_id_f06cbf62;
       public            postgres    false    229            �           1259    44776 5   sms_app_assign_asset_info_AA_asset_number_id_85811802    INDEX     �   CREATE INDEX "sms_app_assign_asset_info_AA_asset_number_id_85811802" ON public.sms_app_assign_asset_info USING btree ("AA_asset_number_id");
 K   DROP INDEX public."sms_app_assign_asset_info_AA_asset_number_id_85811802";
       public            postgres    false    361            �           1259    44769 )   sms_app_bayinfo_Bay_unit_name_id_df361ee2    INDEX     u   CREATE INDEX "sms_app_bayinfo_Bay_unit_name_id_df361ee2" ON public.sms_app_bayinfo USING btree ("Bay_unit_name_id");
 ?   DROP INDEX public."sms_app_bayinfo_Bay_unit_name_id_df361ee2";
       public            postgres    false    233            �           1259    44770 +   sms_app_bayinfo_bay_branch_name_id_400b97bf    INDEX     u   CREATE INDEX sms_app_bayinfo_bay_branch_name_id_400b97bf ON public.sms_app_bayinfo USING btree (bay_branch_name_id);
 ?   DROP INDEX public.sms_app_bayinfo_bay_branch_name_id_400b97bf;
       public            postgres    false    233            �           1259    44767     sms_app_city_country_id_21df082d    INDEX     _   CREATE INDEX sms_app_city_country_id_21df082d ON public.sms_app_city USING btree (country_id);
 4   DROP INDEX public.sms_app_city_country_id_21df082d;
       public            postgres    false    237            �           1259    44768    sms_app_city_state_id_4ee02825    INDEX     [   CREATE INDEX sms_app_city_state_id_4ee02825 ON public.sms_app_city USING btree (state_id);
 2   DROP INDEX public.sms_app_city_state_id_4ee02825;
       public            postgres    false    237            �           1259    44765 5   sms_app_consignmentdetailinfo_co_movement_id_e049ab83    INDEX     �   CREATE INDEX sms_app_consignmentdetailinfo_co_movement_id_e049ab83 ON public.sms_app_consignmentdetailinfo USING btree (co_movement_id);
 I   DROP INDEX public.sms_app_consignmentdetailinfo_co_movement_id_e049ab83;
       public            postgres    false    359            �           1259    44766 3   sms_app_consignmentdetailinfo_co_status_id_0a9b470e    INDEX     �   CREATE INDEX sms_app_consignmentdetailinfo_co_status_id_0a9b470e ON public.sms_app_consignmentdetailinfo USING btree (co_status_id);
 G   DROP INDEX public.sms_app_consignmentdetailinfo_co_status_id_0a9b470e;
       public            postgres    false    359            �           1259    44748 1   sms_app_customerinfo_cu_businessmodel_id_e9d7858e    INDEX     �   CREATE INDEX sms_app_customerinfo_cu_businessmodel_id_e9d7858e ON public.sms_app_customerinfo USING btree (cu_businessmodel_id);
 E   DROP INDEX public.sms_app_customerinfo_cu_businessmodel_id_e9d7858e;
       public            postgres    false    247            �           1259    44749 3   sms_app_customerinfo_cu_creditcountfrom_id_76d1b13a    INDEX     �   CREATE INDEX sms_app_customerinfo_cu_creditcountfrom_id_76d1b13a ON public.sms_app_customerinfo USING btree (cu_creditcountfrom_id);
 G   DROP INDEX public.sms_app_customerinfo_cu_creditcountfrom_id_76d1b13a;
       public            postgres    false    247            �           1259    44750 .   sms_app_customerinfo_cu_department_id_654c73aa    INDEX     {   CREATE INDEX sms_app_customerinfo_cu_department_id_654c73aa ON public.sms_app_customerinfo USING btree (cu_department_id);
 B   DROP INDEX public.sms_app_customerinfo_cu_department_id_654c73aa;
       public            postgres    false    247            �           1259    44751 1   sms_app_customerinfo_cu_gstexcepmtion_id_64756f5a    INDEX     �   CREATE INDEX sms_app_customerinfo_cu_gstexcepmtion_id_64756f5a ON public.sms_app_customerinfo USING btree (cu_gstexcepmtion_id);
 E   DROP INDEX public.sms_app_customerinfo_cu_gstexcepmtion_id_64756f5a;
       public            postgres    false    247            �           1259    44752 ,   sms_app_customerinfo_cu_gstmodel_id_77a5b61f    INDEX     w   CREATE INDEX sms_app_customerinfo_cu_gstmodel_id_77a5b61f ON public.sms_app_customerinfo USING btree (cu_gstmodel_id);
 @   DROP INDEX public.sms_app_customerinfo_cu_gstmodel_id_77a5b61f;
       public            postgres    false    247            �           1259    44753 /   sms_app_customerinfo_cu_paymenttype_id_f7be6e06    INDEX     }   CREATE INDEX sms_app_customerinfo_cu_paymenttype_id_f7be6e06 ON public.sms_app_customerinfo USING btree (cu_paymenttype_id);
 C   DROP INDEX public.sms_app_customerinfo_cu_paymenttype_id_f7be6e06;
       public            postgres    false    247            �           1259    44754 )   sms_app_customerinfo_cu_state_id_f878a950    INDEX     q   CREATE INDEX sms_app_customerinfo_cu_state_id_f878a950 ON public.sms_app_customerinfo USING btree (cu_state_id);
 =   DROP INDEX public.sms_app_customerinfo_cu_state_id_f878a950;
       public            postgres    false    247            �           1259    44790 (   sms_app_customerinfo_cu_type_id_394997bd    INDEX     o   CREATE INDEX sms_app_customerinfo_cu_type_id_394997bd ON public.sms_app_customerinfo USING btree (cu_type_id);
 <   DROP INDEX public.sms_app_customerinfo_cu_type_id_394997bd;
       public            postgres    false    247            |           1259    44746 4   sms_app_damagereportinfo_dam_damage_type_id_343ab67f    INDEX     �   CREATE INDEX sms_app_damagereportinfo_dam_damage_type_id_343ab67f ON public.sms_app_damagereportinfo USING btree (dam_damage_type_id);
 H   DROP INDEX public.sms_app_damagereportinfo_dam_damage_type_id_343ab67f;
       public            postgres    false    357            }           1259    44747 /   sms_app_damagereportinfo_dam_status_id_de711524    INDEX     }   CREATE INDEX sms_app_damagereportinfo_dam_status_id_de711524 ON public.sms_app_damagereportinfo USING btree (dam_status_id);
 C   DROP INDEX public.sms_app_damagereportinfo_dam_status_id_de711524;
       public            postgres    false    357            �           1259    44735 /   sms_app_department_info_dept_status_id_e196a7e5    INDEX     }   CREATE INDEX sms_app_department_info_dept_status_id_e196a7e5 ON public.sms_app_department_info USING btree (dept_status_id);
 C   DROP INDEX public.sms_app_department_info_dept_status_id_e196a7e5;
       public            postgres    false    255            �           1259    45245 4   sms_app_dispatch_info_dispatch_cargo_picked_bbede3e1    INDEX     �   CREATE INDEX sms_app_dispatch_info_dispatch_cargo_picked_bbede3e1 ON public.sms_app_dispatch_info USING btree (dispatch_cargo_picked);
 H   DROP INDEX public.sms_app_dispatch_info_dispatch_cargo_picked_bbede3e1;
       public            postgres    false    377            �           1259    45249 1   sms_app_dispatch_info_dispatch_status_id_aeaa0dbf    INDEX     �   CREATE INDEX sms_app_dispatch_info_dispatch_status_id_aeaa0dbf ON public.sms_app_dispatch_info USING btree (dispatch_status_id);
 E   DROP INDEX public.sms_app_dispatch_info_dispatch_status_id_aeaa0dbf;
       public            postgres    false    377            �           1259    45250 :   sms_app_dispatch_info_dispatch_sticker_pasted_BVM_4c53185e    INDEX     �   CREATE INDEX "sms_app_dispatch_info_dispatch_sticker_pasted_BVM_4c53185e" ON public.sms_app_dispatch_info USING btree ("dispatch_sticker_pasted_BVM");
 P   DROP INDEX public."sms_app_dispatch_info_dispatch_sticker_pasted_BVM_4c53185e";
       public            postgres    false    377            �           1259    45251 5   sms_app_dispatch_info_dispatch_truck_type_id_5d9de5a1    INDEX     �   CREATE INDEX sms_app_dispatch_info_dispatch_truck_type_id_5d9de5a1 ON public.sms_app_dispatch_info USING btree (dispatch_truck_type_id);
 I   DROP INDEX public.sms_app_dispatch_info_dispatch_truck_type_id_5d9de5a1;
       public            postgres    false    377            y           1259    44734 '   sms_app_employee_emp_status_id_5cc7cd0e    INDEX     m   CREATE INDEX sms_app_employee_emp_status_id_5cc7cd0e ON public.sms_app_employee USING btree (emp_status_id);
 ;   DROP INDEX public.sms_app_employee_emp_status_id_5cc7cd0e;
       public            postgres    false    355            o           1259    44721 1   sms_app_enquirynoteinfo_en_assignedto_id_9bccb96f    INDEX     �   CREATE INDEX sms_app_enquirynoteinfo_en_assignedto_id_9bccb96f ON public.sms_app_enquirynoteinfo USING btree (en_assignedto_id);
 E   DROP INDEX public.sms_app_enquirynoteinfo_en_assignedto_id_9bccb96f;
       public            postgres    false    353            p           1259    44722 9   sms_app_enquirynoteinfo_en_customerdepartment_id_a3f3f8af    INDEX     �   CREATE INDEX sms_app_enquirynoteinfo_en_customerdepartment_id_a3f3f8af ON public.sms_app_enquirynoteinfo USING btree (en_customerdepartment_id);
 M   DROP INDEX public.sms_app_enquirynoteinfo_en_customerdepartment_id_a3f3f8af;
       public            postgres    false    353            q           1259    44723 3   sms_app_enquirynoteinfo_en_customername_id_1fa29d25    INDEX     �   CREATE INDEX sms_app_enquirynoteinfo_en_customername_id_1fa29d25 ON public.sms_app_enquirynoteinfo USING btree (en_customername_id);
 G   DROP INDEX public.sms_app_enquirynoteinfo_en_customername_id_1fa29d25;
       public            postgres    false    353            r           1259    44724 /   sms_app_enquirynoteinfo_en_fromlocaion_d867cf38    INDEX     }   CREATE INDEX sms_app_enquirynoteinfo_en_fromlocaion_d867cf38 ON public.sms_app_enquirynoteinfo USING btree (en_fromlocaion);
 C   DROP INDEX public.sms_app_enquirynoteinfo_en_fromlocaion_d867cf38;
       public            postgres    false    353            s           1259    44725 -   sms_app_enquirynoteinfo_en_status_id_a0ed2eff    INDEX     y   CREATE INDEX sms_app_enquirynoteinfo_en_status_id_a0ed2eff ON public.sms_app_enquirynoteinfo USING btree (en_status_id);
 A   DROP INDEX public.sms_app_enquirynoteinfo_en_status_id_a0ed2eff;
       public            postgres    false    353            t           1259    44726 .   sms_app_enquirynoteinfo_en_tolocation_a959565e    INDEX     {   CREATE INDEX sms_app_enquirynoteinfo_en_tolocation_a959565e ON public.sms_app_enquirynoteinfo USING btree (en_tolocation);
 B   DROP INDEX public.sms_app_enquirynoteinfo_en_tolocation_a959565e;
       public            postgres    false    353            u           1259    44727 6   sms_app_enquirynoteinfo_en_vehiclecategory_id_dbc8e2f5    INDEX     �   CREATE INDEX sms_app_enquirynoteinfo_en_vehiclecategory_id_dbc8e2f5 ON public.sms_app_enquirynoteinfo USING btree (en_vehiclecategory_id);
 J   DROP INDEX public.sms_app_enquirynoteinfo_en_vehiclecategory_id_dbc8e2f5;
       public            postgres    false    353            v           1259    44728 2   sms_app_enquirynoteinfo_en_vehicletype_id_5f5c2bea    INDEX     �   CREATE INDEX sms_app_enquirynoteinfo_en_vehicletype_id_5f5c2bea ON public.sms_app_enquirynoteinfo USING btree (en_vehicletype_id);
 F   DROP INDEX public.sms_app_enquirynoteinfo_en_vehicletype_id_5f5c2bea;
       public            postgres    false    353            h           1259    44678 /   sms_app_gatein_info_gatein_customer_id_97b6906c    INDEX     }   CREATE INDEX sms_app_gatein_info_gatein_customer_id_97b6906c ON public.sms_app_gatein_info USING btree (gatein_customer_id);
 C   DROP INDEX public.sms_app_gatein_info_gatein_customer_id_97b6906c;
       public            postgres    false    351            i           1259    44841 4   sms_app_gatein_info_gatein_customer_type_id_fd1762cc    INDEX     �   CREATE INDEX sms_app_gatein_info_gatein_customer_type_id_fd1762cc ON public.sms_app_gatein_info USING btree (gatein_customer_type_id);
 H   DROP INDEX public.sms_app_gatein_info_gatein_customer_type_id_fd1762cc;
       public            postgres    false    351            j           1259    44878 1   sms_app_gatein_info_gatein_department_id_85e1b89e    INDEX     �   CREATE INDEX sms_app_gatein_info_gatein_department_id_85e1b89e ON public.sms_app_gatein_info USING btree (gatein_department_id);
 E   DROP INDEX public.sms_app_gatein_info_gatein_department_id_85e1b89e;
       public            postgres    false    351            k           1259    44679 -   sms_app_gatein_info_gatein_status_id_3184854e    INDEX     y   CREATE INDEX sms_app_gatein_info_gatein_status_id_3184854e ON public.sms_app_gatein_info USING btree (gatein_status_id);
 A   DROP INDEX public.sms_app_gatein_info_gatein_status_id_3184854e;
       public            postgres    false    351            l           1259    44680 1   sms_app_gatein_info_gatein_truck_type_id_442422e0    INDEX     �   CREATE INDEX sms_app_gatein_info_gatein_truck_type_id_442422e0 ON public.sms_app_gatein_info USING btree (gatein_truck_type_id);
 E   DROP INDEX public.sms_app_gatein_info_gatein_truck_type_id_442422e0;
       public            postgres    false    351            c           1259    44660 -   sms_app_insurance_info_ins_status_id_bbc113ca    INDEX     y   CREATE INDEX sms_app_insurance_info_ins_status_id_bbc113ca ON public.sms_app_insurance_info USING btree (ins_status_id);
 A   DROP INDEX public.sms_app_insurance_info_ins_status_id_bbc113ca;
       public            postgres    false    349            d           1259    44661 +   sms_app_insurance_info_ins_type_id_698614d5    INDEX     u   CREATE INDEX sms_app_insurance_info_ins_type_id_698614d5 ON public.sms_app_insurance_info USING btree (ins_type_id);
 ?   DROP INDEX public.sms_app_insurance_info_ins_type_id_698614d5;
       public            postgres    false    349            e           1259    44662 -   sms_app_insurance_info_ins_vendor_id_e8b07566    INDEX     y   CREATE INDEX sms_app_insurance_info_ins_vendor_id_e8b07566 ON public.sms_app_insurance_info USING btree (ins_vendor_id);
 A   DROP INDEX public.sms_app_insurance_info_ins_vendor_id_e8b07566;
       public            postgres    false    349            [           1259    44638 6   sms_app_loadingbay_info_lb_offload_acceptance_27dc9271    INDEX     �   CREATE INDEX sms_app_loadingbay_info_lb_offload_acceptance_27dc9271 ON public.sms_app_loadingbay_info USING btree (lb_offload_acceptance);
 J   DROP INDEX public.sms_app_loadingbay_info_lb_offload_acceptance_27dc9271;
       public            postgres    false    347            \           1259    44639 -   sms_app_loadingbay_info_lb_otl_check_c4448356    INDEX     y   CREATE INDEX sms_app_loadingbay_info_lb_otl_check_c4448356 ON public.sms_app_loadingbay_info USING btree (lb_otl_check);
 A   DROP INDEX public.sms_app_loadingbay_info_lb_otl_check_c4448356;
       public            postgres    false    347            ]           1259    44640 0   sms_app_loadingbay_info_lb_packing_list_3a951df3    INDEX        CREATE INDEX sms_app_loadingbay_info_lb_packing_list_3a951df3 ON public.sms_app_loadingbay_info USING btree (lb_packing_list);
 D   DROP INDEX public.sms_app_loadingbay_info_lb_packing_list_3a951df3;
       public            postgres    false    347            ^           1259    44641 -   sms_app_loadingbay_info_lb_status_id_59ad8c76    INDEX     y   CREATE INDEX sms_app_loadingbay_info_lb_status_id_59ad8c76 ON public.sms_app_loadingbay_info USING btree (lb_status_id);
 A   DROP INDEX public.sms_app_loadingbay_info_lb_status_id_59ad8c76;
       public            postgres    false    347            _           1259    44642 =   sms_app_loadingbay_info_lb_stock_invoice_currency_id_d8774adf    INDEX     �   CREATE INDEX sms_app_loadingbay_info_lb_stock_invoice_currency_id_d8774adf ON public.sms_app_loadingbay_info USING btree (lb_stock_invoice_currency_id);
 Q   DROP INDEX public.sms_app_loadingbay_info_lb_stock_invoice_currency_id_d8774adf;
       public            postgres    false    347            `           1259    44644 1   sms_app_loadingbay_info_lb_stock_type_id_1272b72a    INDEX     �   CREATE INDEX sms_app_loadingbay_info_lb_stock_type_id_1272b72a ON public.sms_app_loadingbay_info USING btree (lb_stock_type_id);
 E   DROP INDEX public.sms_app_loadingbay_info_lb_stock_type_id_1272b72a;
       public            postgres    false    347            �           1259    44204 *   sms_app_location_info_loc_city_id_40800401    INDEX     s   CREATE INDEX sms_app_location_info_loc_city_id_40800401 ON public.sms_app_location_info USING btree (loc_city_id);
 >   DROP INDEX public.sms_app_location_info_loc_city_id_40800401;
       public            postgres    false    269            �           1259    44205 -   sms_app_location_info_loc_country_id_fde4e56f    INDEX     y   CREATE INDEX sms_app_location_info_loc_country_id_fde4e56f ON public.sms_app_location_info USING btree (loc_country_id);
 A   DROP INDEX public.sms_app_location_info_loc_country_id_fde4e56f;
       public            postgres    false    269            �           1259    44595 +   sms_app_location_info_loc_state_id_554baa6c    INDEX     u   CREATE INDEX sms_app_location_info_loc_state_id_554baa6c ON public.sms_app_location_info USING btree (loc_state_id);
 ?   DROP INDEX public.sms_app_location_info_loc_state_id_554baa6c;
       public            postgres    false    269            �           1259    44596 ,   sms_app_location_info_loc_status_id_1e58171a    INDEX     w   CREATE INDEX sms_app_location_info_loc_status_id_1e58171a ON public.sms_app_location_info USING btree (loc_status_id);
 @   DROP INDEX public.sms_app_location_info_loc_status_id_1e58171a;
       public            postgres    false    269            T           1259    44591 2   sms_app_locationmasterinfo_lm_areaside_id_f6464ff2    INDEX     �   CREATE INDEX sms_app_locationmasterinfo_lm_areaside_id_f6464ff2 ON public.sms_app_locationmasterinfo USING btree (lm_areaside_id);
 F   DROP INDEX public.sms_app_locationmasterinfo_lm_areaside_id_f6464ff2;
       public            postgres    false    345            U           1259    45445 8   sms_app_locationmasterinfo_lm_customer_model_id_eab735ca    INDEX     �   CREATE INDEX sms_app_locationmasterinfo_lm_customer_model_id_eab735ca ON public.sms_app_locationmasterinfo USING btree (lm_customer_model_id);
 L   DROP INDEX public.sms_app_locationmasterinfo_lm_customer_model_id_eab735ca;
       public            postgres    false    345            V           1259    44592 7   sms_app_locationmasterinfo_lm_customer_name_id_e11f5787    INDEX     �   CREATE INDEX sms_app_locationmasterinfo_lm_customer_name_id_e11f5787 ON public.sms_app_locationmasterinfo USING btree (lm_customer_name_id);
 K   DROP INDEX public.sms_app_locationmasterinfo_lm_customer_name_id_e11f5787;
       public            postgres    false    345            W           1259    44593 5   sms_app_locationmasterinfo_lm_wh_location_id_24bd1aec    INDEX     �   CREATE INDEX sms_app_locationmasterinfo_lm_wh_location_id_24bd1aec ON public.sms_app_locationmasterinfo USING btree (lm_wh_location_id);
 I   DROP INDEX public.sms_app_locationmasterinfo_lm_wh_location_id_24bd1aec;
       public            postgres    false    345            X           1259    44594 1   sms_app_locationmasterinfo_lm_wh_unit_id_28c94bef    INDEX     �   CREATE INDEX sms_app_locationmasterinfo_lm_wh_unit_id_28c94bef ON public.sms_app_locationmasterinfo USING btree (lm_wh_unit_id);
 E   DROP INDEX public.sms_app_locationmasterinfo_lm_wh_unit_id_28c94bef;
       public            postgres    false    345            S           1259    44570 *   sms_app_product_info_prod_type_id_6aef937d    INDEX     s   CREATE INDEX sms_app_product_info_prod_type_id_6aef937d ON public.sms_app_product_info USING btree (prod_type_id);
 >   DROP INDEX public.sms_app_product_info_prod_type_id_6aef937d;
       public            postgres    false    343            L           1259    44560 0   sms_app_rtratemasterinfo_ro_customer_id_9033887c    INDEX        CREATE INDEX sms_app_rtratemasterinfo_ro_customer_id_9033887c ON public.sms_app_rtratemasterinfo USING btree (ro_customer_id);
 D   DROP INDEX public.sms_app_rtratemasterinfo_ro_customer_id_9033887c;
       public            postgres    false    341            M           1259    44561 :   sms_app_rtratemasterinfo_ro_customerdepartment_id_502dac20    INDEX     �   CREATE INDEX sms_app_rtratemasterinfo_ro_customerdepartment_id_502dac20 ON public.sms_app_rtratemasterinfo USING btree (ro_customerdepartment_id);
 N   DROP INDEX public.sms_app_rtratemasterinfo_ro_customerdepartment_id_502dac20;
       public            postgres    false    341            N           1259    44562 1   sms_app_rtratemasterinfo_ro_fromlocation_3c20f564    INDEX     �   CREATE INDEX sms_app_rtratemasterinfo_ro_fromlocation_3c20f564 ON public.sms_app_rtratemasterinfo USING btree (ro_fromlocation);
 E   DROP INDEX public.sms_app_rtratemasterinfo_ro_fromlocation_3c20f564;
       public            postgres    false    341            O           1259    44563 /   sms_app_rtratemasterinfo_ro_tolocation_41d78ea7    INDEX     }   CREATE INDEX sms_app_rtratemasterinfo_ro_tolocation_41d78ea7 ON public.sms_app_rtratemasterinfo USING btree (ro_tolocation);
 C   DROP INDEX public.sms_app_rtratemasterinfo_ro_tolocation_41d78ea7;
       public            postgres    false    341            P           1259    44564 0   sms_app_rtratemasterinfo_ro_vehicletype_1fdd5564    INDEX        CREATE INDEX sms_app_rtratemasterinfo_ro_vehicletype_1fdd5564 ON public.sms_app_rtratemasterinfo USING btree (ro_vehicletype);
 D   DROP INDEX public.sms_app_rtratemasterinfo_ro_vehicletype_1fdd5564;
       public            postgres    false    341            G           1259    44532 *   sms_app_service_info_ser_asset_id_71b67a00    INDEX     s   CREATE INDEX sms_app_service_info_ser_asset_id_71b67a00 ON public.sms_app_service_info USING btree (ser_asset_id);
 >   DROP INDEX public.sms_app_service_info_ser_asset_id_71b67a00;
       public            postgres    false    339            H           1259    44533 +   sms_app_service_info_ser_status_id_c02692d9    INDEX     u   CREATE INDEX sms_app_service_info_ser_status_id_c02692d9 ON public.sms_app_service_info USING btree (ser_status_id);
 ?   DROP INDEX public.sms_app_service_info_ser_status_id_c02692d9;
       public            postgres    false    339            I           1259    44534 +   sms_app_service_info_ser_vendor_id_37f6cd0a    INDEX     u   CREATE INDEX sms_app_service_info_ser_vendor_id_37f6cd0a ON public.sms_app_service_info USING btree (ser_vendor_id);
 ?   DROP INDEX public.sms_app_service_info_ser_vendor_id_37f6cd0a;
       public            postgres    false    339            �           1259    44211 !   sms_app_state_country_id_582603f1    INDEX     a   CREATE INDEX sms_app_state_country_id_582603f1 ON public.sms_app_state USING btree (country_id);
 5   DROP INDEX public.sms_app_state_country_id_582603f1;
       public            postgres    false    291            D           1259    44516 4   sms_app_tripclosureinfo_tc_financestatus_id_2178aaad    INDEX     �   CREATE INDEX sms_app_tripclosureinfo_tc_financestatus_id_2178aaad ON public.sms_app_tripclosureinfo USING btree (tc_financestatus_id);
 H   DROP INDEX public.sms_app_tripclosureinfo_tc_financestatus_id_2178aaad;
       public            postgres    false    337            >           1259    44507 /   sms_app_tripdetailinfo_tr_fromlocation_87cf2d65    INDEX     }   CREATE INDEX sms_app_tripdetailinfo_tr_fromlocation_87cf2d65 ON public.sms_app_tripdetailinfo USING btree (tr_fromlocation);
 C   DROP INDEX public.sms_app_tripdetailinfo_tr_fromlocation_87cf2d65;
       public            postgres    false    335            ?           1259    44508 )   sms_app_tripdetailinfo_tr_status_6d0945d4    INDEX     q   CREATE INDEX sms_app_tripdetailinfo_tr_status_6d0945d4 ON public.sms_app_tripdetailinfo USING btree (tr_status);
 =   DROP INDEX public.sms_app_tripdetailinfo_tr_status_6d0945d4;
       public            postgres    false    335            @           1259    44509 -   sms_app_tripdetailinfo_tr_tolocation_2f56a91e    INDEX     y   CREATE INDEX sms_app_tripdetailinfo_tr_tolocation_2f56a91e ON public.sms_app_tripdetailinfo USING btree (tr_tolocation);
 A   DROP INDEX public.sms_app_tripdetailinfo_tr_tolocation_2f56a91e;
       public            postgres    false    335            A           1259    44510 -   sms_app_tripdetailinfo_tr_tripstatus_12f6f382    INDEX     y   CREATE INDEX sms_app_tripdetailinfo_tr_tripstatus_12f6f382 ON public.sms_app_tripdetailinfo USING btree (tr_tripstatus);
 A   DROP INDEX public.sms_app_tripdetailinfo_tr_tripstatus_12f6f382;
       public            postgres    false    335            �           1259    44217 +   sms_app_unitinfo_ui_branch_name_id_e57ac2eb    INDEX     u   CREATE INDEX sms_app_unitinfo_ui_branch_name_id_e57ac2eb ON public.sms_app_unitinfo USING btree (ui_branch_name_id);
 ?   DROP INDEX public.sms_app_unitinfo_ui_branch_name_id_e57ac2eb;
       public            postgres    false    303            4           1259    44483 +   sms_app_user_extinfo_department_id_5e767fc2    INDEX     u   CREATE INDEX sms_app_user_extinfo_department_id_5e767fc2 ON public.sms_app_user_extinfo USING btree (department_id);
 ?   DROP INDEX public.sms_app_user_extinfo_department_id_5e767fc2;
       public            postgres    false    333            5           1259    44484 +   sms_app_user_extinfo_emp_branch_id_88f377a7    INDEX     u   CREATE INDEX sms_app_user_extinfo_emp_branch_id_88f377a7 ON public.sms_app_user_extinfo USING btree (emp_branch_id);
 ?   DROP INDEX public.sms_app_user_extinfo_emp_branch_id_88f377a7;
       public            postgres    false    333            6           1259    44485 0   sms_app_user_extinfo_emp_designation_id_7570dc8c    INDEX        CREATE INDEX sms_app_user_extinfo_emp_designation_id_7570dc8c ON public.sms_app_user_extinfo USING btree (emp_designation_id);
 D   DROP INDEX public.sms_app_user_extinfo_emp_designation_id_7570dc8c;
       public            postgres    false    333            7           1259    44486 )   sms_app_user_extinfo_emp_role_id_49a48d91    INDEX     q   CREATE INDEX sms_app_user_extinfo_emp_role_id_49a48d91 ON public.sms_app_user_extinfo USING btree (emp_role_id);
 =   DROP INDEX public.sms_app_user_extinfo_emp_role_id_49a48d91;
       public            postgres    false    333            /           1259    44453 /   sms_app_vehicledetailinfo_ve_status_id_bc19131e    INDEX     }   CREATE INDEX sms_app_vehicledetailinfo_ve_status_id_bc19131e ON public.sms_app_vehicledetailinfo USING btree (ve_status_id);
 C   DROP INDEX public.sms_app_vehicledetailinfo_ve_status_id_bc19131e;
       public            postgres    false    331            0           1259    44454 >   sms_app_vehicledetailinfo_ve_transportbusinesstype_id_434e2791    INDEX     �   CREATE INDEX sms_app_vehicledetailinfo_ve_transportbusinesstype_id_434e2791 ON public.sms_app_vehicledetailinfo USING btree (ve_transportbusinesstype_id);
 R   DROP INDEX public.sms_app_vehicledetailinfo_ve_transportbusinesstype_id_434e2791;
       public            postgres    false    331            1           1259    44455 6   sms_app_vehicledetailinfo_ve_vehiclenumber_id_ace702ff    INDEX     �   CREATE INDEX sms_app_vehicledetailinfo_ve_vehiclenumber_id_ace702ff ON public.sms_app_vehicledetailinfo USING btree (ve_vehiclenumber_id);
 J   DROP INDEX public.sms_app_vehicledetailinfo_ve_vehiclenumber_id_ace702ff;
       public            postgres    false    331            2           1259    44456 6   sms_app_vehicledetailinfo_ve_vehiclesource_id_b018706a    INDEX     �   CREATE INDEX sms_app_vehicledetailinfo_ve_vehiclesource_id_b018706a ON public.sms_app_vehicledetailinfo USING btree (ve_vehiclesource_id);
 J   DROP INDEX public.sms_app_vehicledetailinfo_ve_vehiclesource_id_b018706a;
       public            postgres    false    331            3           1259    44457 4   sms_app_vehicledetailinfo_ve_vehicletype_id_9a270b16    INDEX     �   CREATE INDEX sms_app_vehicledetailinfo_ve_vehicletype_id_9a270b16 ON public.sms_app_vehicledetailinfo USING btree (ve_vehicletype_id);
 H   DROP INDEX public.sms_app_vehicledetailinfo_ve_vehicletype_id_9a270b16;
       public            postgres    false    331                       1259    44413 1   sms_app_vehiclemasterinfo_vm_axletype_id_f999b0d8    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_axletype_id_f999b0d8 ON public.sms_app_vehiclemasterinfo USING btree (vm_axletype_id);
 E   DROP INDEX public.sms_app_vehiclemasterinfo_vm_axletype_id_f999b0d8;
       public            postgres    false    329                       1259    44414 -   sms_app_vehiclemasterinfo_vm_body_id_ed5a47f4    INDEX     y   CREATE INDEX sms_app_vehiclemasterinfo_vm_body_id_ed5a47f4 ON public.sms_app_vehiclemasterinfo USING btree (vm_body_id);
 A   DROP INDEX public.sms_app_vehiclemasterinfo_vm_body_id_ed5a47f4;
       public            postgres    false    329                        1259    44415 ,   sms_app_vehiclemasterinfo_vm_fccopy_861967bc    INDEX     w   CREATE INDEX sms_app_vehiclemasterinfo_vm_fccopy_861967bc ON public.sms_app_vehiclemasterinfo USING btree (vm_fccopy);
 @   DROP INDEX public.sms_app_vehiclemasterinfo_vm_fccopy_861967bc;
       public            postgres    false    329            !           1259    44416 1   sms_app_vehiclemasterinfo_vm_fueltype_id_07779033    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_fueltype_id_07779033 ON public.sms_app_vehiclemasterinfo USING btree (vm_fueltype_id);
 E   DROP INDEX public.sms_app_vehiclemasterinfo_vm_fueltype_id_07779033;
       public            postgres    false    329            "           1259    44417 3   sms_app_vehiclemasterinfo_vm_insurancecopy_a3c7467e    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_insurancecopy_a3c7467e ON public.sms_app_vehiclemasterinfo USING btree (vm_insurancecopy);
 G   DROP INDEX public.sms_app_vehiclemasterinfo_vm_insurancecopy_a3c7467e;
       public            postgres    false    329            #           1259    44418 6   sms_app_vehiclemasterinfo_vm_insurancetype_id_0b857e64    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_insurancetype_id_0b857e64 ON public.sms_app_vehiclemasterinfo USING btree (vm_insurancetype_id);
 J   DROP INDEX public.sms_app_vehiclemasterinfo_vm_insurancetype_id_0b857e64;
       public            postgres    false    329            $           1259    44419 2   sms_app_vehiclemasterinfo_vm_ownership_id_9caf41ab    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_ownership_id_9caf41ab ON public.sms_app_vehiclemasterinfo USING btree (vm_ownership_id);
 F   DROP INDEX public.sms_app_vehiclemasterinfo_vm_ownership_id_9caf41ab;
       public            postgres    false    329            %           1259    44420 0   sms_app_vehiclemasterinfo_vm_permitcopy_b5175b20    INDEX        CREATE INDEX sms_app_vehiclemasterinfo_vm_permitcopy_b5175b20 ON public.sms_app_vehiclemasterinfo USING btree (vm_permitcopy);
 D   DROP INDEX public.sms_app_vehiclemasterinfo_vm_permitcopy_b5175b20;
       public            postgres    false    329            &           1259    44421 3   sms_app_vehiclemasterinfo_vm_permittype_id_628a1204    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_permittype_id_628a1204 ON public.sms_app_vehiclemasterinfo USING btree (vm_permittype_id);
 G   DROP INDEX public.sms_app_vehiclemasterinfo_vm_permittype_id_628a1204;
       public            postgres    false    329            '           1259    44422 >   sms_app_vehiclemasterinfo_vm_pollutioncertificatecopy_3649ebd6    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_pollutioncertificatecopy_3649ebd6 ON public.sms_app_vehiclemasterinfo USING btree (vm_pollutioncertificatecopy);
 R   DROP INDEX public.sms_app_vehiclemasterinfo_vm_pollutioncertificatecopy_3649ebd6;
       public            postgres    false    329            (           1259    44423 1   sms_app_vehiclemasterinfo_vm_roadtaxcopy_146527b2    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_roadtaxcopy_146527b2 ON public.sms_app_vehiclemasterinfo USING btree (vm_roadtaxcopy);
 E   DROP INDEX public.sms_app_vehiclemasterinfo_vm_roadtaxcopy_146527b2;
       public            postgres    false    329            )           1259    44424 6   sms_app_vehiclemasterinfo_vm_vehiclecolour_id_a642af05    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_vehiclecolour_id_a642af05 ON public.sms_app_vehiclemasterinfo USING btree (vm_vehiclecolour_id);
 J   DROP INDEX public.sms_app_vehiclemasterinfo_vm_vehiclecolour_id_a642af05;
       public            postgres    false    329            *           1259    44425 <   sms_app_vehiclemasterinfo_vm_vehiclemanufacturer_id_9fd4d2e3    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_vehiclemanufacturer_id_9fd4d2e3 ON public.sms_app_vehiclemasterinfo USING btree (vm_vehiclemanufacturer_id);
 P   DROP INDEX public.sms_app_vehiclemasterinfo_vm_vehiclemanufacturer_id_9fd4d2e3;
       public            postgres    false    329            +           1259    44426 5   sms_app_vehiclemasterinfo_vm_vehiclemodel_id_9c42182e    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_vehiclemodel_id_9c42182e ON public.sms_app_vehiclemasterinfo USING btree (vm_vehiclemodel_id);
 I   DROP INDEX public.sms_app_vehiclemasterinfo_vm_vehiclemodel_id_9c42182e;
       public            postgres    false    329            ,           1259    44427 4   sms_app_vehiclemasterinfo_vm_vehicletype_id_4bd552f3    INDEX     �   CREATE INDEX sms_app_vehiclemasterinfo_vm_vehicletype_id_4bd552f3 ON public.sms_app_vehiclemasterinfo USING btree (vm_vehicletype_id);
 H   DROP INDEX public.sms_app_vehiclemasterinfo_vm_vehicletype_id_4bd552f3;
       public            postgres    false    329                       1259    44334 )   sms_app_vendor_info_vend_city_id_81197869    INDEX     q   CREATE INDEX sms_app_vendor_info_vend_city_id_81197869 ON public.sms_app_vendor_info USING btree (vend_city_id);
 =   DROP INDEX public.sms_app_vendor_info_vend_city_id_81197869;
       public            postgres    false    327                       1259    44335 ,   sms_app_vendor_info_vend_country_id_23d99c63    INDEX     w   CREATE INDEX sms_app_vendor_info_vend_country_id_23d99c63 ON public.sms_app_vendor_info USING btree (vend_country_id);
 @   DROP INDEX public.sms_app_vendor_info_vend_country_id_23d99c63;
       public            postgres    false    327                       1259    44336 *   sms_app_vendor_info_vend_state_id_15b81b8a    INDEX     s   CREATE INDEX sms_app_vendor_info_vend_state_id_15b81b8a ON public.sms_app_vendor_info USING btree (vend_state_id);
 >   DROP INDEX public.sms_app_vendor_info_vend_state_id_15b81b8a;
       public            postgres    false    327                       1259    44337 +   sms_app_vendor_info_vend_status_id_659d6836    INDEX     u   CREATE INDEX sms_app_vendor_info_vend_status_id_659d6836 ON public.sms_app_vendor_info USING btree (vend_status_id);
 ?   DROP INDEX public.sms_app_vendor_info_vend_status_id_659d6836;
       public            postgres    false    327                       1259    44302 /   sms_app_warehouse_goods_info_wh_bay_id_88ec3542    INDEX     }   CREATE INDEX sms_app_warehouse_goods_info_wh_bay_id_88ec3542 ON public.sms_app_warehouse_goods_info USING btree (wh_bay_id);
 C   DROP INDEX public.sms_app_warehouse_goods_info_wh_bay_id_88ec3542;
       public            postgres    false    325            	           1259    44303 2   sms_app_warehouse_goods_info_wh_branch_id_22da1bdf    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_branch_id_22da1bdf ON public.sms_app_warehouse_goods_info USING btree (wh_branch_id);
 F   DROP INDEX public.sms_app_warehouse_goods_info_wh_branch_id_22da1bdf;
       public            postgres    false    325            
           1259    44304 5   sms_app_warehouse_goods_info_wh_check_in_out_32f33d72    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_check_in_out_32f33d72 ON public.sms_app_warehouse_goods_info USING btree (wh_check_in_out);
 I   DROP INDEX public.sms_app_warehouse_goods_info_wh_check_in_out_32f33d72;
       public            postgres    false    325                       1259    44305 0   sms_app_warehouse_goods_info_wh_damages_5ae02b46    INDEX        CREATE INDEX sms_app_warehouse_goods_info_wh_damages_5ae02b46 ON public.sms_app_warehouse_goods_info USING btree (wh_damages);
 D   DROP INDEX public.sms_app_warehouse_goods_info_wh_damages_5ae02b46;
       public            postgres    false    325                       1259    44306 <   sms_app_warehouse_goods_info_wh_dimension_deviation_ea172824    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_dimension_deviation_ea172824 ON public.sms_app_warehouse_goods_info USING btree (wh_dimension_deviation);
 P   DROP INDEX public.sms_app_warehouse_goods_info_wh_dimension_deviation_ea172824;
       public            postgres    false    325                       1259    44307 >   sms_app_warehouse_goods_info_wh_goods_package_type_id_7fb626b6    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_goods_package_type_id_7fb626b6 ON public.sms_app_warehouse_goods_info USING btree (wh_goods_package_type_id);
 R   DROP INDEX public.sms_app_warehouse_goods_info_wh_goods_package_type_id_7fb626b6;
       public            postgres    false    325                       1259    44308 5   sms_app_warehouse_goods_info_wh_goods_status_2b2f2d3e    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_goods_status_2b2f2d3e ON public.sms_app_warehouse_goods_info USING btree (wh_goods_status);
 I   DROP INDEX public.sms_app_warehouse_goods_info_wh_goods_status_2b2f2d3e;
       public            postgres    false    325                       1259    44309 3   sms_app_warehouse_goods_info_wh_mismatches_3d25aae9    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_mismatches_3d25aae9 ON public.sms_app_warehouse_goods_info USING btree (wh_mismatches);
 G   DROP INDEX public.sms_app_warehouse_goods_info_wh_mismatches_3d25aae9;
       public            postgres    false    325                       1259    44310 >   sms_app_warehouse_goods_info_wh_no_of_units_deviation_29467fea    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_no_of_units_deviation_29467fea ON public.sms_app_warehouse_goods_info USING btree (wh_no_of_units_deviation);
 R   DROP INDEX public.sms_app_warehouse_goods_info_wh_no_of_units_deviation_29467fea;
       public            postgres    false    325                       1259    44311 =   sms_app_warehouse_goods_info_wh_ratification_process_ea24e93f    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_ratification_process_ea24e93f ON public.sms_app_warehouse_goods_info USING btree (wh_ratification_process);
 Q   DROP INDEX public.sms_app_warehouse_goods_info_wh_ratification_process_ea24e93f;
       public            postgres    false    325                       1259    45202 7   sms_app_warehouse_goods_info_wh_stack_layer_id_daed76f2    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_stack_layer_id_daed76f2 ON public.sms_app_warehouse_goods_info USING btree (wh_stack_layer_id);
 K   DROP INDEX public.sms_app_warehouse_goods_info_wh_stack_layer_id_daed76f2;
       public            postgres    false    325                       1259    44312 0   sms_app_warehouse_goods_info_wh_unit_id_3db59ae9    INDEX        CREATE INDEX sms_app_warehouse_goods_info_wh_unit_id_3db59ae9 ON public.sms_app_warehouse_goods_info USING btree (wh_unit_id);
 D   DROP INDEX public.sms_app_warehouse_goods_info_wh_unit_id_3db59ae9;
       public            postgres    false    325                       1259    44956 ,   sms_app_warehouse_goods_info_wh_uom_6b2e57d0    INDEX     w   CREATE INDEX sms_app_warehouse_goods_info_wh_uom_6b2e57d0 ON public.sms_app_warehouse_goods_info USING btree (wh_uom);
 @   DROP INDEX public.sms_app_warehouse_goods_info_wh_uom_6b2e57d0;
       public            postgres    false    325                       1259    44313 :   sms_app_warehouse_goods_info_wh_weights_deviation_d741d34a    INDEX     �   CREATE INDEX sms_app_warehouse_goods_info_wh_weights_deviation_d741d34a ON public.sms_app_warehouse_goods_info USING btree (wh_weights_deviation);
 N   DROP INDEX public.sms_app_warehouse_goods_info_wh_weights_deviation_d741d34a;
       public            postgres    false    325                       1259    44239 >   sms_app_warehouse_stock_in_wh_stock_invoice_currency__36d2be16    INDEX     �   CREATE INDEX sms_app_warehouse_stock_in_wh_stock_invoice_currency__36d2be16 ON public.sms_app_warehouse_stock_info USING btree (wh_stock_invoice_currency_id);
 R   DROP INDEX public.sms_app_warehouse_stock_in_wh_stock_invoice_currency__36d2be16;
       public            postgres    false    323                       1259    44240 ?   sms_app_warehouse_stock_info_wh_stock_movement_type_id_0488da2a    INDEX     �   CREATE INDEX sms_app_warehouse_stock_info_wh_stock_movement_type_id_0488da2a ON public.sms_app_warehouse_stock_info USING btree (wh_stock_movement_type_id);
 S   DROP INDEX public.sms_app_warehouse_stock_info_wh_stock_movement_type_id_0488da2a;
       public            postgres    false    323                       1259    44241 6   sms_app_warehouse_stock_info_wh_stock_type_id_6ffa2856    INDEX     �   CREATE INDEX sms_app_warehouse_stock_info_wh_stock_type_id_6ffa2856 ON public.sms_app_warehouse_stock_info USING btree (wh_stock_type_id);
 J   DROP INDEX public.sms_app_warehouse_stock_info_wh_stock_type_id_6ffa2856;
       public            postgres    false    323                        1259    44223 6   sms_app_whratemasterinfo_whrm_storage_type_id_ec3f552d    INDEX     �   CREATE INDEX sms_app_whratemasterinfo_whrm_storage_type_id_ec3f552d ON public.sms_app_whratemasterinfo USING btree (whrm_storage_type_id);
 J   DROP INDEX public.sms_app_whratemasterinfo_whrm_storage_type_id_ec3f552d;
       public            postgres    false    321            �           2606    43540 O   auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
       public          postgres    false    3684    218    214            �           2606    43535 P   auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
       public          postgres    false    216    218    3689            �           2606    43526 E   auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co;
       public          postgres    false    214    3679    212            �           2606    43555 D   auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 n   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id;
       public          postgres    false    222    216    3689            �           2606    43550 B   auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id;
       public          postgres    false    3697    220    222            �           2606    43569 S   auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm;
       public          postgres    false    224    214    3684            �           2606    43564 V   auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id;
       public          postgres    false    220    224    3697            �           2606    43586 G   django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co;
       public          postgres    false    3679    212    226            �           2606    43591 B   django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id;
       public          postgres    false    3697    226    220            �           2606    44164 P   sms_app_assetinfo sms_app_assetinfo_asset_assignedto_id_f44be589_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_assetinfo
    ADD CONSTRAINT sms_app_assetinfo_asset_assignedto_id_f44be589_fk_auth_user_id FOREIGN KEY (asset_assignedto_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.sms_app_assetinfo DROP CONSTRAINT sms_app_assetinfo_asset_assignedto_id_f44be589_fk_auth_user_id;
       public          postgres    false    229    220    3697            �           2606    44169 N   sms_app_assetinfo sms_app_assetinfo_asset_insurance_deta_ca581a27_fk_sms_app_i    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_assetinfo
    ADD CONSTRAINT sms_app_assetinfo_asset_insurance_deta_ca581a27_fk_sms_app_i FOREIGN KEY (asset_insurance_details_id) REFERENCES public.sms_app_insurance_info(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.sms_app_assetinfo DROP CONSTRAINT sms_app_assetinfo_asset_insurance_deta_ca581a27_fk_sms_app_i;
       public          postgres    false    229    349    3943            �           2606    44174 K   sms_app_assetinfo sms_app_assetinfo_asset_location_id_8a72cb33_fk_sms_app_l    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_assetinfo
    ADD CONSTRAINT sms_app_assetinfo_asset_location_id_8a72cb33_fk_sms_app_l FOREIGN KEY (asset_location_id) REFERENCES public.sms_app_location_info(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.sms_app_assetinfo DROP CONSTRAINT sms_app_assetinfo_asset_location_id_8a72cb33_fk_sms_app_l;
       public          postgres    false    229    269    3785            �           2606    44179 J   sms_app_assetinfo sms_app_assetinfo_asset_product_id_4a65faf4_fk_sms_app_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_assetinfo
    ADD CONSTRAINT sms_app_assetinfo_asset_product_id_4a65faf4_fk_sms_app_p FOREIGN KEY (asset_product_id) REFERENCES public.sms_app_product_info(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.sms_app_assetinfo DROP CONSTRAINT sms_app_assetinfo_asset_product_id_4a65faf4_fk_sms_app_p;
       public          postgres    false    343    3922    229            �           2606    44184 Q   sms_app_assetinfo sms_app_assetinfo_asset_unit_id_3ce46701_fk_sms_app_unitinfo_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_assetinfo
    ADD CONSTRAINT sms_app_assetinfo_asset_unit_id_3ce46701_fk_sms_app_unitinfo_id FOREIGN KEY (asset_unit_id) REFERENCES public.sms_app_unitinfo(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_assetinfo DROP CONSTRAINT sms_app_assetinfo_asset_unit_id_3ce46701_fk_sms_app_unitinfo_id;
       public          postgres    false    229    303    3820            �           2606    44189 I   sms_app_assetinfo sms_app_assetinfo_asset_vendor_id_f06cbf62_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_assetinfo
    ADD CONSTRAINT sms_app_assetinfo_asset_vendor_id_f06cbf62_fk_sms_app_v FOREIGN KEY (asset_vendor_id) REFERENCES public.sms_app_vendor_info(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.sms_app_assetinfo DROP CONSTRAINT sms_app_assetinfo_asset_vendor_id_f06cbf62_fk_sms_app_v;
       public          postgres    false    229    327    3863                       2606    44771 W   sms_app_assign_asset_info sms_app_assign_asset_AA_asset_number_id_85811802_fk_sms_app_a    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_assign_asset_info
    ADD CONSTRAINT "sms_app_assign_asset_AA_asset_number_id_85811802_fk_sms_app_a" FOREIGN KEY ("AA_asset_number_id") REFERENCES public.sms_app_assetinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_assign_asset_info DROP CONSTRAINT "sms_app_assign_asset_AA_asset_number_id_85811802_fk_sms_app_a";
       public          postgres    false    229    361    3728            �           2606    44147 F   sms_app_bayinfo sms_app_bayinfo_Bay_unit_name_id_df361ee2_fk_sms_app_u    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_bayinfo
    ADD CONSTRAINT "sms_app_bayinfo_Bay_unit_name_id_df361ee2_fk_sms_app_u" FOREIGN KEY ("Bay_unit_name_id") REFERENCES public.sms_app_unitinfo(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.sms_app_bayinfo DROP CONSTRAINT "sms_app_bayinfo_Bay_unit_name_id_df361ee2_fk_sms_app_u";
       public          postgres    false    233    3820    303            �           2606    44152 H   sms_app_bayinfo sms_app_bayinfo_bay_branch_name_id_400b97bf_fk_sms_app_l    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_bayinfo
    ADD CONSTRAINT sms_app_bayinfo_bay_branch_name_id_400b97bf_fk_sms_app_l FOREIGN KEY (bay_branch_name_id) REFERENCES public.sms_app_location_info(id) DEFERRABLE INITIALLY DEFERRED;
 r   ALTER TABLE ONLY public.sms_app_bayinfo DROP CONSTRAINT sms_app_bayinfo_bay_branch_name_id_400b97bf_fk_sms_app_l;
       public          postgres    false    233    269    3785            �           2606    44137 C   sms_app_city sms_app_city_country_id_21df082d_fk_sms_app_country_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_city
    ADD CONSTRAINT sms_app_city_country_id_21df082d_fk_sms_app_country_id FOREIGN KEY (country_id) REFERENCES public.sms_app_country(id) DEFERRABLE INITIALLY DEFERRED;
 m   ALTER TABLE ONLY public.sms_app_city DROP CONSTRAINT sms_app_city_country_id_21df082d_fk_sms_app_country_id;
       public          postgres    false    239    237    3742            �           2606    44142 ?   sms_app_city sms_app_city_state_id_4ee02825_fk_sms_app_state_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_city
    ADD CONSTRAINT sms_app_city_state_id_4ee02825_fk_sms_app_state_id FOREIGN KEY (state_id) REFERENCES public.sms_app_state(id) DEFERRABLE INITIALLY DEFERRED;
 i   ALTER TABLE ONLY public.sms_app_city DROP CONSTRAINT sms_app_city_state_id_4ee02825_fk_sms_app_state_id;
       public          postgres    false    3808    291    237                       2606    44755 W   sms_app_consignmentdetailinfo sms_app_consignmentd_co_movement_id_e049ab83_fk_sms_app_m    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_consignmentdetailinfo
    ADD CONSTRAINT sms_app_consignmentd_co_movement_id_e049ab83_fk_sms_app_m FOREIGN KEY (co_movement_id) REFERENCES public.sms_app_movementtypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_consignmentdetailinfo DROP CONSTRAINT sms_app_consignmentd_co_movement_id_e049ab83_fk_sms_app_m;
       public          postgres    false    273    3789    359                       2606    44760 U   sms_app_consignmentdetailinfo sms_app_consignmentd_co_status_id_0a9b470e_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_consignmentdetailinfo
    ADD CONSTRAINT sms_app_consignmentd_co_status_id_0a9b470e_fk_sms_app_s FOREIGN KEY (co_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_consignmentdetailinfo DROP CONSTRAINT sms_app_consignmentd_co_status_id_0a9b470e_fk_sms_app_s;
       public          postgres    false    3810    359    293            �           2606    44095 S   sms_app_customerinfo sms_app_customerinfo_cu_businessmodel_id_e9d7858e_fk_sms_app_t    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_businessmodel_id_e9d7858e_fk_sms_app_t FOREIGN KEY (cu_businessmodel_id) REFERENCES public.sms_app_trbusinesstypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_businessmodel_id_e9d7858e_fk_sms_app_t;
       public          postgres    false    247    3818    301            �           2606    44100 T   sms_app_customerinfo sms_app_customerinfo_cu_creditcountfrom_i_76d1b13a_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_creditcountfrom_i_76d1b13a_fk_sms_app_c FOREIGN KEY (cu_creditcountfrom_id) REFERENCES public.sms_app_crcountfrominfo(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_creditcountfrom_i_76d1b13a_fk_sms_app_c;
       public          postgres    false    241    3744    247            �           2606    44105 P   sms_app_customerinfo sms_app_customerinfo_cu_department_id_654c73aa_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_department_id_654c73aa_fk_sms_app_c FOREIGN KEY (cu_department_id) REFERENCES public.sms_app_customerdepartmentinfo(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_department_id_654c73aa_fk_sms_app_c;
       public          postgres    false    3748    247    245            �           2606    44110 S   sms_app_customerinfo sms_app_customerinfo_cu_gstexcepmtion_id_64756f5a_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_gstexcepmtion_id_64756f5a_fk_sms_app_g FOREIGN KEY (cu_gstexcepmtion_id) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_gstexcepmtion_id_64756f5a_fk_sms_app_g;
       public          postgres    false    263    247    3775            �           2606    44115 N   sms_app_customerinfo sms_app_customerinfo_cu_gstmodel_id_77a5b61f_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_gstmodel_id_77a5b61f_fk_sms_app_g FOREIGN KEY (cu_gstmodel_id) REFERENCES public.sms_app_gstmodelinfo(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_gstmodel_id_77a5b61f_fk_sms_app_g;
       public          postgres    false    3777    247    265            �           2606    44120 Q   sms_app_customerinfo sms_app_customerinfo_cu_paymenttype_id_f7be6e06_fk_sms_app_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_paymenttype_id_f7be6e06_fk_sms_app_p FOREIGN KEY (cu_paymenttype_id) REFERENCES public.sms_app_paymenttypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_paymenttype_id_f7be6e06_fk_sms_app_p;
       public          postgres    false    247    279    3795            �           2606    44125 R   sms_app_customerinfo sms_app_customerinfo_cu_state_id_f878a950_fk_sms_app_state_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_state_id_f878a950_fk_sms_app_state_id FOREIGN KEY (cu_state_id) REFERENCES public.sms_app_state(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_state_id_f878a950_fk_sms_app_state_id;
       public          postgres    false    3808    291    247            �           2606    44785 J   sms_app_customerinfo sms_app_customerinfo_cu_type_id_394997bd_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_customerinfo
    ADD CONSTRAINT sms_app_customerinfo_cu_type_id_394997bd_fk_sms_app_c FOREIGN KEY (cu_type_id) REFERENCES public.sms_app_customertypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.sms_app_customerinfo DROP CONSTRAINT sms_app_customerinfo_cu_type_id_394997bd_fk_sms_app_c;
       public          postgres    false    3762    247    251                       2606    45102 V   sms_app_damagereportinfo sms_app_damagereport_dam_damage_type_id_343ab67f_fk_sms_app_d    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_damagereportinfo
    ADD CONSTRAINT sms_app_damagereport_dam_damage_type_id_343ab67f_fk_sms_app_d FOREIGN KEY (dam_damage_type_id) REFERENCES public.sms_app_damageinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_damagereportinfo DROP CONSTRAINT sms_app_damagereport_dam_damage_type_id_343ab67f_fk_sms_app_d;
       public          postgres    false    3764    253    357                       2606    44741 Q   sms_app_damagereportinfo sms_app_damagereport_dam_status_id_de711524_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_damagereportinfo
    ADD CONSTRAINT sms_app_damagereport_dam_status_id_de711524_fk_sms_app_s FOREIGN KEY (dam_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_damagereportinfo DROP CONSTRAINT sms_app_damagereport_dam_status_id_de711524_fk_sms_app_s;
       public          postgres    false    357    3810    293            �           2606    45145 Q   sms_app_department_info sms_app_department_i_dept_status_id_e196a7e5_fk_sms_app_a    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_department_info
    ADD CONSTRAINT sms_app_department_i_dept_status_id_e196a7e5_fk_sms_app_a FOREIGN KEY (dept_status_id) REFERENCES public.sms_app_activeinactiveinfo(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_department_info DROP CONSTRAINT sms_app_department_i_dept_status_id_e196a7e5_fk_sms_app_a;
       public          postgres    false    255    3986    373                       2606    45210 U   sms_app_dispatch_info sms_app_dispatch_inf_dispatch_cargo_picke_bbede3e1_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_dispatch_info
    ADD CONSTRAINT sms_app_dispatch_inf_dispatch_cargo_picke_bbede3e1_fk_sms_app_g FOREIGN KEY (dispatch_cargo_picked) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_dispatch_info DROP CONSTRAINT sms_app_dispatch_inf_dispatch_cargo_picke_bbede3e1_fk_sms_app_g;
       public          postgres    false    3775    377    263                       2606    45230 S   sms_app_dispatch_info sms_app_dispatch_inf_dispatch_status_id_aeaa0dbf_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_dispatch_info
    ADD CONSTRAINT sms_app_dispatch_inf_dispatch_status_id_aeaa0dbf_fk_sms_app_s FOREIGN KEY (dispatch_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_dispatch_info DROP CONSTRAINT sms_app_dispatch_inf_dispatch_status_id_aeaa0dbf_fk_sms_app_s;
       public          postgres    false    3810    377    293                       2606    45235 U   sms_app_dispatch_info sms_app_dispatch_inf_dispatch_sticker_pas_4c53185e_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_dispatch_info
    ADD CONSTRAINT sms_app_dispatch_inf_dispatch_sticker_pas_4c53185e_fk_sms_app_g FOREIGN KEY ("dispatch_sticker_pasted_BVM") REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_dispatch_info DROP CONSTRAINT sms_app_dispatch_inf_dispatch_sticker_pas_4c53185e_fk_sms_app_g;
       public          postgres    false    377    3775    263                        2606    45240 U   sms_app_dispatch_info sms_app_dispatch_inf_dispatch_truck_type__5d9de5a1_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_dispatch_info
    ADD CONSTRAINT sms_app_dispatch_inf_dispatch_truck_type__5d9de5a1_fk_sms_app_v FOREIGN KEY (dispatch_truck_type_id) REFERENCES public.sms_app_vehicletypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_dispatch_info DROP CONSTRAINT sms_app_dispatch_inf_dispatch_truck_type__5d9de5a1_fk_sms_app_v;
       public          postgres    false    377    3833    315                       2606    44729 E   sms_app_employee sms_app_employee_emp_status_id_5cc7cd0e_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_employee
    ADD CONSTRAINT sms_app_employee_emp_status_id_5cc7cd0e_fk_sms_app_s FOREIGN KEY (emp_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.sms_app_employee DROP CONSTRAINT sms_app_employee_emp_status_id_5cc7cd0e_fk_sms_app_s;
       public          postgres    false    3810    293    355                       2606    44681 S   sms_app_enquirynoteinfo sms_app_enquirynotei_en_assignedto_id_9bccb96f_fk_auth_user    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_assignedto_id_9bccb96f_fk_auth_user FOREIGN KEY (en_assignedto_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_assignedto_id_9bccb96f_fk_auth_user;
       public          postgres    false    220    353    3697                       2606    44686 W   sms_app_enquirynoteinfo sms_app_enquirynotei_en_customerdepartmen_a3f3f8af_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_customerdepartmen_a3f3f8af_fk_sms_app_c FOREIGN KEY (en_customerdepartment_id) REFERENCES public.sms_app_customerdepartmentinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_customerdepartmen_a3f3f8af_fk_sms_app_c;
       public          postgres    false    3748    353    245                       2606    44691 U   sms_app_enquirynoteinfo sms_app_enquirynotei_en_customername_id_1fa29d25_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_customername_id_1fa29d25_fk_sms_app_c FOREIGN KEY (en_customername_id) REFERENCES public.sms_app_customerinfo(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_customername_id_1fa29d25_fk_sms_app_c;
       public          postgres    false    247    353    3758                       2606    44696 Q   sms_app_enquirynoteinfo sms_app_enquirynotei_en_fromlocaion_d867cf38_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_fromlocaion_d867cf38_fk_sms_app_c FOREIGN KEY (en_fromlocaion) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_fromlocaion_d867cf38_fk_sms_app_c;
       public          postgres    false    237    3739    353                       2606    44701 O   sms_app_enquirynoteinfo sms_app_enquirynotei_en_status_id_a0ed2eff_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_status_id_a0ed2eff_fk_sms_app_s FOREIGN KEY (en_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_status_id_a0ed2eff_fk_sms_app_s;
       public          postgres    false    293    353    3810                       2606    44706 P   sms_app_enquirynoteinfo sms_app_enquirynotei_en_tolocation_a959565e_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_tolocation_a959565e_fk_sms_app_c FOREIGN KEY (en_tolocation) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_tolocation_a959565e_fk_sms_app_c;
       public          postgres    false    237    353    3739                       2606    44711 W   sms_app_enquirynoteinfo sms_app_enquirynotei_en_vehiclecategory_i_dbc8e2f5_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_vehiclecategory_i_dbc8e2f5_fk_sms_app_v FOREIGN KEY (en_vehiclecategory_id) REFERENCES public.sms_app_vehiclecategoryinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_vehiclecategory_i_dbc8e2f5_fk_sms_app_v;
       public          postgres    false    3823    353    305                       2606    44716 T   sms_app_enquirynoteinfo sms_app_enquirynotei_en_vehicletype_id_5f5c2bea_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_enquirynoteinfo
    ADD CONSTRAINT sms_app_enquirynotei_en_vehicletype_id_5f5c2bea_fk_sms_app_v FOREIGN KEY (en_vehicletype_id) REFERENCES public.sms_app_vehicletypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.sms_app_enquirynoteinfo DROP CONSTRAINT sms_app_enquirynotei_en_vehicletype_id_5f5c2bea_fk_sms_app_v;
       public          postgres    false    3833    353    315            
           2606    44663 P   sms_app_gatein_info sms_app_gatein_info_gatein_customer_id_97b6906c_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_gatein_info
    ADD CONSTRAINT sms_app_gatein_info_gatein_customer_id_97b6906c_fk_sms_app_c FOREIGN KEY (gatein_customer_id) REFERENCES public.sms_app_customerinfo(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.sms_app_gatein_info DROP CONSTRAINT sms_app_gatein_info_gatein_customer_id_97b6906c_fk_sms_app_c;
       public          postgres    false    247    351    3758                       2606    44842 R   sms_app_gatein_info sms_app_gatein_info_gatein_customer_type_fd1762cc_fk_sms_app_t    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_gatein_info
    ADD CONSTRAINT sms_app_gatein_info_gatein_customer_type_fd1762cc_fk_sms_app_t FOREIGN KEY (gatein_customer_type_id) REFERENCES public.sms_app_trbusinesstypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_gatein_info DROP CONSTRAINT sms_app_gatein_info_gatein_customer_type_fd1762cc_fk_sms_app_t;
       public          postgres    false    351    301    3818                       2606    44879 R   sms_app_gatein_info sms_app_gatein_info_gatein_department_id_85e1b89e_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_gatein_info
    ADD CONSTRAINT sms_app_gatein_info_gatein_department_id_85e1b89e_fk_sms_app_c FOREIGN KEY (gatein_department_id) REFERENCES public.sms_app_customerdepartmentinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_gatein_info DROP CONSTRAINT sms_app_gatein_info_gatein_department_id_85e1b89e_fk_sms_app_c;
       public          postgres    false    3748    351    245                       2606    44668 N   sms_app_gatein_info sms_app_gatein_info_gatein_status_id_3184854e_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_gatein_info
    ADD CONSTRAINT sms_app_gatein_info_gatein_status_id_3184854e_fk_sms_app_s FOREIGN KEY (gatein_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.sms_app_gatein_info DROP CONSTRAINT sms_app_gatein_info_gatein_status_id_3184854e_fk_sms_app_s;
       public          postgres    false    3810    293    351                       2606    44673 R   sms_app_gatein_info sms_app_gatein_info_gatein_truck_type_id_442422e0_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_gatein_info
    ADD CONSTRAINT sms_app_gatein_info_gatein_truck_type_id_442422e0_fk_sms_app_v FOREIGN KEY (gatein_truck_type_id) REFERENCES public.sms_app_vehicletypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_gatein_info DROP CONSTRAINT sms_app_gatein_info_gatein_truck_type_id_442422e0_fk_sms_app_v;
       public          postgres    false    351    315    3833                       2606    44645 O   sms_app_insurance_info sms_app_insurance_in_ins_status_id_bbc113ca_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_insurance_info
    ADD CONSTRAINT sms_app_insurance_in_ins_status_id_bbc113ca_fk_sms_app_s FOREIGN KEY (ins_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_insurance_info DROP CONSTRAINT sms_app_insurance_in_ins_status_id_bbc113ca_fk_sms_app_s;
       public          postgres    false    3810    293    349                       2606    44650 M   sms_app_insurance_info sms_app_insurance_in_ins_type_id_698614d5_fk_sms_app_i    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_insurance_info
    ADD CONSTRAINT sms_app_insurance_in_ins_type_id_698614d5_fk_sms_app_i FOREIGN KEY (ins_type_id) REFERENCES public.sms_app_insurance_type(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.sms_app_insurance_info DROP CONSTRAINT sms_app_insurance_in_ins_type_id_698614d5_fk_sms_app_i;
       public          postgres    false    349    3779    267            	           2606    44655 O   sms_app_insurance_info sms_app_insurance_in_ins_vendor_id_e8b07566_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_insurance_info
    ADD CONSTRAINT sms_app_insurance_in_ins_vendor_id_e8b07566_fk_sms_app_v FOREIGN KEY (ins_vendor_id) REFERENCES public.sms_app_vendor_info(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_insurance_info DROP CONSTRAINT sms_app_insurance_in_ins_vendor_id_e8b07566_fk_sms_app_v;
       public          postgres    false    327    349    3863                       2606    45491 W   sms_app_loadingbay_info sms_app_loadingbay_i_lb_offload_acceptanc_27dc9271_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_loadingbay_info
    ADD CONSTRAINT sms_app_loadingbay_i_lb_offload_acceptanc_27dc9271_fk_sms_app_g FOREIGN KEY (lb_offload_acceptance) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_loadingbay_info DROP CONSTRAINT sms_app_loadingbay_i_lb_offload_acceptanc_27dc9271_fk_sms_app_g;
       public          postgres    false    347    3775    263                       2606    45496 O   sms_app_loadingbay_info sms_app_loadingbay_i_lb_otl_check_c4448356_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_loadingbay_info
    ADD CONSTRAINT sms_app_loadingbay_i_lb_otl_check_c4448356_fk_sms_app_g FOREIGN KEY (lb_otl_check) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_loadingbay_info DROP CONSTRAINT sms_app_loadingbay_i_lb_otl_check_c4448356_fk_sms_app_g;
       public          postgres    false    263    3775    347                       2606    45056 R   sms_app_loadingbay_info sms_app_loadingbay_i_lb_packing_list_3a951df3_fk_sms_app_r    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_loadingbay_info
    ADD CONSTRAINT sms_app_loadingbay_i_lb_packing_list_3a951df3_fk_sms_app_r FOREIGN KEY (lb_packing_list) REFERENCES public.sms_app_received_not(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_loadingbay_info DROP CONSTRAINT sms_app_loadingbay_i_lb_packing_list_3a951df3_fk_sms_app_r;
       public          postgres    false    347    3980    367                       2606    44617 O   sms_app_loadingbay_info sms_app_loadingbay_i_lb_status_id_59ad8c76_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_loadingbay_info
    ADD CONSTRAINT sms_app_loadingbay_i_lb_status_id_59ad8c76_fk_sms_app_s FOREIGN KEY (lb_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_loadingbay_info DROP CONSTRAINT sms_app_loadingbay_i_lb_status_id_59ad8c76_fk_sms_app_s;
       public          postgres    false    293    347    3810                       2606    44622 W   sms_app_loadingbay_info sms_app_loadingbay_i_lb_stock_invoice_cur_d8774adf_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_loadingbay_info
    ADD CONSTRAINT sms_app_loadingbay_i_lb_stock_invoice_cur_d8774adf_fk_sms_app_c FOREIGN KEY (lb_stock_invoice_currency_id) REFERENCES public.sms_app_currency_type(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_loadingbay_info DROP CONSTRAINT sms_app_loadingbay_i_lb_stock_invoice_cur_d8774adf_fk_sms_app_c;
       public          postgres    false    243    347    3746                       2606    44632 S   sms_app_loadingbay_info sms_app_loadingbay_i_lb_stock_type_id_1272b72a_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_loadingbay_info
    ADD CONSTRAINT sms_app_loadingbay_i_lb_stock_type_id_1272b72a_fk_sms_app_s FOREIGN KEY (lb_stock_type_id) REFERENCES public.sms_app_stock_type(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_loadingbay_info DROP CONSTRAINT sms_app_loadingbay_i_lb_stock_type_id_1272b72a_fk_sms_app_s;
       public          postgres    false    3814    347    297            �           2606    44199 O   sms_app_location_info sms_app_location_inf_loc_country_id_fde4e56f_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_location_info
    ADD CONSTRAINT sms_app_location_inf_loc_country_id_fde4e56f_fk_sms_app_c FOREIGN KEY (loc_country_id) REFERENCES public.sms_app_country(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_location_info DROP CONSTRAINT sms_app_location_inf_loc_country_id_fde4e56f_fk_sms_app_c;
       public          postgres    false    239    269    3742            �           2606    45150 N   sms_app_location_info sms_app_location_inf_loc_status_id_1e58171a_fk_sms_app_a    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_location_info
    ADD CONSTRAINT sms_app_location_inf_loc_status_id_1e58171a_fk_sms_app_a FOREIGN KEY (loc_status_id) REFERENCES public.sms_app_activeinactiveinfo(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.sms_app_location_info DROP CONSTRAINT sms_app_location_inf_loc_status_id_1e58171a_fk_sms_app_a;
       public          postgres    false    373    269    3986            �           2606    44194 S   sms_app_location_info sms_app_location_info_loc_city_id_40800401_fk_sms_app_city_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_location_info
    ADD CONSTRAINT sms_app_location_info_loc_city_id_40800401_fk_sms_app_city_id FOREIGN KEY (loc_city_id) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_location_info DROP CONSTRAINT sms_app_location_info_loc_city_id_40800401_fk_sms_app_city_id;
       public          postgres    false    269    3739    237            �           2606    44036 U   sms_app_location_info sms_app_location_info_loc_state_id_554baa6c_fk_sms_app_state_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_location_info
    ADD CONSTRAINT sms_app_location_info_loc_state_id_554baa6c_fk_sms_app_state_id FOREIGN KEY (loc_state_id) REFERENCES public.sms_app_state(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_location_info DROP CONSTRAINT sms_app_location_info_loc_state_id_554baa6c_fk_sms_app_state_id;
       public          postgres    false    3808    291    269            �           2606    44571 T   sms_app_locationmasterinfo sms_app_locationmast_lm_areaside_id_f6464ff2_fk_sms_app_b    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_locationmasterinfo
    ADD CONSTRAINT sms_app_locationmast_lm_areaside_id_f6464ff2_fk_sms_app_b FOREIGN KEY (lm_areaside_id) REFERENCES public.sms_app_bayinfo(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.sms_app_locationmasterinfo DROP CONSTRAINT sms_app_locationmast_lm_areaside_id_f6464ff2_fk_sms_app_b;
       public          postgres    false    3734    233    345                        2606    45446 Z   sms_app_locationmasterinfo sms_app_locationmast_lm_customer_model_id_eab735ca_fk_sms_app_t    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_locationmasterinfo
    ADD CONSTRAINT sms_app_locationmast_lm_customer_model_id_eab735ca_fk_sms_app_t FOREIGN KEY (lm_customer_model_id) REFERENCES public.sms_app_trbusinesstypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_locationmasterinfo DROP CONSTRAINT sms_app_locationmast_lm_customer_model_id_eab735ca_fk_sms_app_t;
       public          postgres    false    301    345    3818            �           2606    44576 Y   sms_app_locationmasterinfo sms_app_locationmast_lm_customer_name_id_e11f5787_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_locationmasterinfo
    ADD CONSTRAINT sms_app_locationmast_lm_customer_name_id_e11f5787_fk_sms_app_c FOREIGN KEY (lm_customer_name_id) REFERENCES public.sms_app_customerinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_locationmasterinfo DROP CONSTRAINT sms_app_locationmast_lm_customer_name_id_e11f5787_fk_sms_app_c;
       public          postgres    false    3758    345    247            �           2606    44581 W   sms_app_locationmasterinfo sms_app_locationmast_lm_wh_location_id_24bd1aec_fk_sms_app_l    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_locationmasterinfo
    ADD CONSTRAINT sms_app_locationmast_lm_wh_location_id_24bd1aec_fk_sms_app_l FOREIGN KEY (lm_wh_location_id) REFERENCES public.sms_app_location_info(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_locationmasterinfo DROP CONSTRAINT sms_app_locationmast_lm_wh_location_id_24bd1aec_fk_sms_app_l;
       public          postgres    false    3785    269    345            �           2606    44586 S   sms_app_locationmasterinfo sms_app_locationmast_lm_wh_unit_id_28c94bef_fk_sms_app_u    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_locationmasterinfo
    ADD CONSTRAINT sms_app_locationmast_lm_wh_unit_id_28c94bef_fk_sms_app_u FOREIGN KEY (lm_wh_unit_id) REFERENCES public.sms_app_unitinfo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_locationmasterinfo DROP CONSTRAINT sms_app_locationmast_lm_wh_unit_id_28c94bef_fk_sms_app_u;
       public          postgres    false    345    303    3820            �           2606    44565 L   sms_app_product_info sms_app_product_info_prod_type_id_6aef937d_fk_sms_app_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_product_info
    ADD CONSTRAINT sms_app_product_info_prod_type_id_6aef937d_fk_sms_app_p FOREIGN KEY (prod_type_id) REFERENCES public.sms_app_prod_type(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.sms_app_product_info DROP CONSTRAINT sms_app_product_info_prod_type_id_6aef937d_fk_sms_app_p;
       public          postgres    false    3803    343    287            �           2606    44535 R   sms_app_rtratemasterinfo sms_app_rtratemaster_ro_customer_id_9033887c_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_rtratemasterinfo
    ADD CONSTRAINT sms_app_rtratemaster_ro_customer_id_9033887c_fk_sms_app_c FOREIGN KEY (ro_customer_id) REFERENCES public.sms_app_customerinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_rtratemasterinfo DROP CONSTRAINT sms_app_rtratemaster_ro_customer_id_9033887c_fk_sms_app_c;
       public          postgres    false    247    341    3758            �           2606    44540 X   sms_app_rtratemasterinfo sms_app_rtratemaster_ro_customerdepartmen_502dac20_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_rtratemasterinfo
    ADD CONSTRAINT sms_app_rtratemaster_ro_customerdepartmen_502dac20_fk_sms_app_c FOREIGN KEY (ro_customerdepartment_id) REFERENCES public.sms_app_customerdepartmentinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_rtratemasterinfo DROP CONSTRAINT sms_app_rtratemaster_ro_customerdepartmen_502dac20_fk_sms_app_c;
       public          postgres    false    245    3748    341            �           2606    44545 S   sms_app_rtratemasterinfo sms_app_rtratemaster_ro_fromlocation_3c20f564_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_rtratemasterinfo
    ADD CONSTRAINT sms_app_rtratemaster_ro_fromlocation_3c20f564_fk_sms_app_c FOREIGN KEY (ro_fromlocation) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_rtratemasterinfo DROP CONSTRAINT sms_app_rtratemaster_ro_fromlocation_3c20f564_fk_sms_app_c;
       public          postgres    false    237    3739    341            �           2606    44550 Q   sms_app_rtratemasterinfo sms_app_rtratemaster_ro_tolocation_41d78ea7_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_rtratemasterinfo
    ADD CONSTRAINT sms_app_rtratemaster_ro_tolocation_41d78ea7_fk_sms_app_c FOREIGN KEY (ro_tolocation) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_rtratemasterinfo DROP CONSTRAINT sms_app_rtratemaster_ro_tolocation_41d78ea7_fk_sms_app_c;
       public          postgres    false    341    3739    237            �           2606    44555 R   sms_app_rtratemasterinfo sms_app_rtratemaster_ro_vehicletype_1fdd5564_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_rtratemasterinfo
    ADD CONSTRAINT sms_app_rtratemaster_ro_vehicletype_1fdd5564_fk_sms_app_v FOREIGN KEY (ro_vehicletype) REFERENCES public.sms_app_vehicletypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_rtratemasterinfo DROP CONSTRAINT sms_app_rtratemaster_ro_vehicletype_1fdd5564_fk_sms_app_v;
       public          postgres    false    3833    315    341            �           2606    44517 L   sms_app_service_info sms_app_service_info_ser_asset_id_71b67a00_fk_sms_app_a    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_service_info
    ADD CONSTRAINT sms_app_service_info_ser_asset_id_71b67a00_fk_sms_app_a FOREIGN KEY (ser_asset_id) REFERENCES public.sms_app_assetinfo(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.sms_app_service_info DROP CONSTRAINT sms_app_service_info_ser_asset_id_71b67a00_fk_sms_app_a;
       public          postgres    false    229    3728    339            �           2606    44522 M   sms_app_service_info sms_app_service_info_ser_status_id_c02692d9_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_service_info
    ADD CONSTRAINT sms_app_service_info_ser_status_id_c02692d9_fk_sms_app_s FOREIGN KEY (ser_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.sms_app_service_info DROP CONSTRAINT sms_app_service_info_ser_status_id_c02692d9_fk_sms_app_s;
       public          postgres    false    3810    293    339            �           2606    44527 M   sms_app_service_info sms_app_service_info_ser_vendor_id_37f6cd0a_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_service_info
    ADD CONSTRAINT sms_app_service_info_ser_vendor_id_37f6cd0a_fk_sms_app_v FOREIGN KEY (ser_vendor_id) REFERENCES public.sms_app_vendor_info(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.sms_app_service_info DROP CONSTRAINT sms_app_service_info_ser_vendor_id_37f6cd0a_fk_sms_app_v;
       public          postgres    false    3863    327    339            �           2606    44206 E   sms_app_state sms_app_state_country_id_582603f1_fk_sms_app_country_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_state
    ADD CONSTRAINT sms_app_state_country_id_582603f1_fk_sms_app_country_id FOREIGN KEY (country_id) REFERENCES public.sms_app_country(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.sms_app_state DROP CONSTRAINT sms_app_state_country_id_582603f1_fk_sms_app_country_id;
       public          postgres    false    291    239    3742            �           2606    44511 V   sms_app_tripclosureinfo sms_app_tripclosurei_tc_financestatus_id_2178aaad_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_tripclosureinfo
    ADD CONSTRAINT sms_app_tripclosurei_tc_financestatus_id_2178aaad_fk_sms_app_s FOREIGN KEY (tc_financestatus_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_tripclosureinfo DROP CONSTRAINT sms_app_tripclosurei_tc_financestatus_id_2178aaad_fk_sms_app_s;
       public          postgres    false    293    3810    337            �           2606    44487 Q   sms_app_tripdetailinfo sms_app_tripdetailin_tr_fromlocation_87cf2d65_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_tripdetailinfo
    ADD CONSTRAINT sms_app_tripdetailin_tr_fromlocation_87cf2d65_fk_sms_app_c FOREIGN KEY (tr_fromlocation) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_tripdetailinfo DROP CONSTRAINT sms_app_tripdetailin_tr_fromlocation_87cf2d65_fk_sms_app_c;
       public          postgres    false    237    3739    335            �           2606    44492 K   sms_app_tripdetailinfo sms_app_tripdetailin_tr_status_6d0945d4_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_tripdetailinfo
    ADD CONSTRAINT sms_app_tripdetailin_tr_status_6d0945d4_fk_sms_app_s FOREIGN KEY (tr_status) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.sms_app_tripdetailinfo DROP CONSTRAINT sms_app_tripdetailin_tr_status_6d0945d4_fk_sms_app_s;
       public          postgres    false    293    3810    335            �           2606    44497 O   sms_app_tripdetailinfo sms_app_tripdetailin_tr_tolocation_2f56a91e_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_tripdetailinfo
    ADD CONSTRAINT sms_app_tripdetailin_tr_tolocation_2f56a91e_fk_sms_app_c FOREIGN KEY (tr_tolocation) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_tripdetailinfo DROP CONSTRAINT sms_app_tripdetailin_tr_tolocation_2f56a91e_fk_sms_app_c;
       public          postgres    false    237    335    3739            �           2606    44502 O   sms_app_tripdetailinfo sms_app_tripdetailin_tr_tripstatus_12f6f382_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_tripdetailinfo
    ADD CONSTRAINT sms_app_tripdetailin_tr_tripstatus_12f6f382_fk_sms_app_s FOREIGN KEY (tr_tripstatus) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_tripdetailinfo DROP CONSTRAINT sms_app_tripdetailin_tr_tripstatus_12f6f382_fk_sms_app_s;
       public          postgres    false    293    3810    335            �           2606    44212 I   sms_app_unitinfo sms_app_unitinfo_ui_branch_name_id_e57ac2eb_fk_sms_app_l    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_unitinfo
    ADD CONSTRAINT sms_app_unitinfo_ui_branch_name_id_e57ac2eb_fk_sms_app_l FOREIGN KEY (ui_branch_name_id) REFERENCES public.sms_app_location_info(id) DEFERRABLE INITIALLY DEFERRED;
 s   ALTER TABLE ONLY public.sms_app_unitinfo DROP CONSTRAINT sms_app_unitinfo_ui_branch_name_id_e57ac2eb_fk_sms_app_l;
       public          postgres    false    3785    303    269            �           2606    44458 M   sms_app_user_extinfo sms_app_user_extinfo_department_id_5e767fc2_fk_sms_app_d    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_user_extinfo
    ADD CONSTRAINT sms_app_user_extinfo_department_id_5e767fc2_fk_sms_app_d FOREIGN KEY (department_id) REFERENCES public.sms_app_department_info(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.sms_app_user_extinfo DROP CONSTRAINT sms_app_user_extinfo_department_id_5e767fc2_fk_sms_app_d;
       public          postgres    false    255    333    3767            �           2606    44463 M   sms_app_user_extinfo sms_app_user_extinfo_emp_branch_id_88f377a7_fk_sms_app_l    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_user_extinfo
    ADD CONSTRAINT sms_app_user_extinfo_emp_branch_id_88f377a7_fk_sms_app_l FOREIGN KEY (emp_branch_id) REFERENCES public.sms_app_location_info(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.sms_app_user_extinfo DROP CONSTRAINT sms_app_user_extinfo_emp_branch_id_88f377a7_fk_sms_app_l;
       public          postgres    false    333    269    3785            �           2606    44468 R   sms_app_user_extinfo sms_app_user_extinfo_emp_designation_id_7570dc8c_fk_sms_app_d    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_user_extinfo
    ADD CONSTRAINT sms_app_user_extinfo_emp_designation_id_7570dc8c_fk_sms_app_d FOREIGN KEY (emp_designation_id) REFERENCES public.sms_app_designationinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_user_extinfo DROP CONSTRAINT sms_app_user_extinfo_emp_designation_id_7570dc8c_fk_sms_app_d;
       public          postgres    false    257    333    3769            �           2606    44473 K   sms_app_user_extinfo sms_app_user_extinfo_emp_role_id_49a48d91_fk_sms_app_r    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_user_extinfo
    ADD CONSTRAINT sms_app_user_extinfo_emp_role_id_49a48d91_fk_sms_app_r FOREIGN KEY (emp_role_id) REFERENCES public.sms_app_roleinfo(id) DEFERRABLE INITIALLY DEFERRED;
 u   ALTER TABLE ONLY public.sms_app_user_extinfo DROP CONSTRAINT sms_app_user_extinfo_emp_role_id_49a48d91_fk_sms_app_r;
       public          postgres    false    289    333    3805            �           2606    44478 J   sms_app_user_extinfo sms_app_user_extinfo_user_id_b0223060_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_user_extinfo
    ADD CONSTRAINT sms_app_user_extinfo_user_id_b0223060_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 t   ALTER TABLE ONLY public.sms_app_user_extinfo DROP CONSTRAINT sms_app_user_extinfo_user_id_b0223060_fk_auth_user_id;
       public          postgres    false    3697    333    220            �           2606    44428 Q   sms_app_vehicledetailinfo sms_app_vehicledetai_ve_status_id_bc19131e_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo
    ADD CONSTRAINT sms_app_vehicledetai_ve_status_id_bc19131e_fk_sms_app_s FOREIGN KEY (ve_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_vehicledetailinfo DROP CONSTRAINT sms_app_vehicledetai_ve_status_id_bc19131e_fk_sms_app_s;
       public          postgres    false    3810    331    293            �           2606    44433 Y   sms_app_vehicledetailinfo sms_app_vehicledetai_ve_transportbusiness_434e2791_fk_sms_app_t    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo
    ADD CONSTRAINT sms_app_vehicledetai_ve_transportbusiness_434e2791_fk_sms_app_t FOREIGN KEY (ve_transportbusinesstype_id) REFERENCES public.sms_app_trbusinesstypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo DROP CONSTRAINT sms_app_vehicledetai_ve_transportbusiness_434e2791_fk_sms_app_t;
       public          postgres    false    331    3818    301            �           2606    44438 X   sms_app_vehicledetailinfo sms_app_vehicledetai_ve_vehiclenumber_id_ace702ff_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo
    ADD CONSTRAINT sms_app_vehicledetai_ve_vehiclenumber_id_ace702ff_fk_sms_app_v FOREIGN KEY (ve_vehiclenumber_id) REFERENCES public.sms_app_vehiclenumberinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo DROP CONSTRAINT sms_app_vehicledetai_ve_vehiclenumber_id_ace702ff_fk_sms_app_v;
       public          postgres    false    3829    311    331            �           2606    44443 X   sms_app_vehicledetailinfo sms_app_vehicledetai_ve_vehiclesource_id_b018706a_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo
    ADD CONSTRAINT sms_app_vehicledetai_ve_vehiclesource_id_b018706a_fk_sms_app_v FOREIGN KEY (ve_vehiclesource_id) REFERENCES public.sms_app_vehiclesourceinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo DROP CONSTRAINT sms_app_vehicledetai_ve_vehiclesource_id_b018706a_fk_sms_app_v;
       public          postgres    false    331    3831    313            �           2606    44448 V   sms_app_vehicledetailinfo sms_app_vehicledetai_ve_vehicletype_id_9a270b16_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo
    ADD CONSTRAINT sms_app_vehicledetai_ve_vehicletype_id_9a270b16_fk_sms_app_v FOREIGN KEY (ve_vehicletype_id) REFERENCES public.sms_app_vehicletypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehicledetailinfo DROP CONSTRAINT sms_app_vehicledetai_ve_vehicletype_id_9a270b16_fk_sms_app_v;
       public          postgres    false    331    3833    315            �           2606    44338 S   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_axletype_id_f999b0d8_fk_sms_app_a    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_axletype_id_f999b0d8_fk_sms_app_a FOREIGN KEY (vm_axletype_id) REFERENCES public.sms_app_axletypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_axletype_id_f999b0d8_fk_sms_app_a;
       public          postgres    false    329    231    3730            �           2606    44343 O   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_body_id_ed5a47f4_fk_sms_app_b    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_body_id_ed5a47f4_fk_sms_app_b FOREIGN KEY (vm_body_id) REFERENCES public.sms_app_bodyinfo(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_body_id_ed5a47f4_fk_sms_app_b;
       public          postgres    false    329    235    3736            �           2606    44348 N   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_fccopy_861967bc_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_fccopy_861967bc_fk_sms_app_s FOREIGN KEY (vm_fccopy) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 x   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_fccopy_861967bc_fk_sms_app_s;
       public          postgres    false    3810    293    329            �           2606    44353 S   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_fueltype_id_07779033_fk_sms_app_f    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_fueltype_id_07779033_fk_sms_app_f FOREIGN KEY (vm_fueltype_id) REFERENCES public.sms_app_fueltypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_fueltype_id_07779033_fk_sms_app_f;
       public          postgres    false    261    329    3773            �           2606    44358 U   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_insurancecopy_a3c7467e_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_insurancecopy_a3c7467e_fk_sms_app_s FOREIGN KEY (vm_insurancecopy) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_insurancecopy_a3c7467e_fk_sms_app_s;
       public          postgres    false    3810    329    293            �           2606    44363 X   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_insurancetype_id_0b857e64_fk_sms_app_i    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_insurancetype_id_0b857e64_fk_sms_app_i FOREIGN KEY (vm_insurancetype_id) REFERENCES public.sms_app_insurance_type(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_insurancetype_id_0b857e64_fk_sms_app_i;
       public          postgres    false    3779    267    329            �           2606    44368 T   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_ownership_id_9caf41ab_fk_sms_app_o    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_ownership_id_9caf41ab_fk_sms_app_o FOREIGN KEY (vm_ownership_id) REFERENCES public.sms_app_ownershipinfo(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_ownership_id_9caf41ab_fk_sms_app_o;
       public          postgres    false    3791    329    275            �           2606    44373 R   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_permitcopy_b5175b20_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_permitcopy_b5175b20_fk_sms_app_s FOREIGN KEY (vm_permitcopy) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_permitcopy_b5175b20_fk_sms_app_s;
       public          postgres    false    329    3810    293            �           2606    44378 U   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_permittype_id_628a1204_fk_sms_app_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_permittype_id_628a1204_fk_sms_app_p FOREIGN KEY (vm_permittype_id) REFERENCES public.sms_app_permittypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_permittype_id_628a1204_fk_sms_app_p;
       public          postgres    false    329    3799    283            �           2606    44383 Y   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_pollutioncertific_3649ebd6_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_pollutioncertific_3649ebd6_fk_sms_app_s FOREIGN KEY (vm_pollutioncertificatecopy) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_pollutioncertific_3649ebd6_fk_sms_app_s;
       public          postgres    false    329    3810    293            �           2606    44388 S   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_roadtaxcopy_146527b2_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_roadtaxcopy_146527b2_fk_sms_app_s FOREIGN KEY (vm_roadtaxcopy) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_roadtaxcopy_146527b2_fk_sms_app_s;
       public          postgres    false    329    293    3810            �           2606    44393 X   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_vehiclecolour_id_a642af05_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_vehiclecolour_id_a642af05_fk_sms_app_v FOREIGN KEY (vm_vehiclecolour_id) REFERENCES public.sms_app_vehiclecolourinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_vehiclecolour_id_a642af05_fk_sms_app_v;
       public          postgres    false    329    3825    307            �           2606    44398 Y   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_vehiclemanufactur_9fd4d2e3_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_vehiclemanufactur_9fd4d2e3_fk_sms_app_v FOREIGN KEY (vm_vehiclemanufacturer_id) REFERENCES public.sms_app_vhmanufacturerinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_vehiclemanufactur_9fd4d2e3_fk_sms_app_v;
       public          postgres    false    329    3835    317            �           2606    44403 W   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_vehiclemodel_id_9c42182e_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_vehiclemodel_id_9c42182e_fk_sms_app_v FOREIGN KEY (vm_vehiclemodel_id) REFERENCES public.sms_app_vehiclemodelinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_vehiclemodel_id_9c42182e_fk_sms_app_v;
       public          postgres    false    329    309    3827            �           2606    44408 V   sms_app_vehiclemasterinfo sms_app_vehiclemaste_vm_vehicletype_id_4bd552f3_fk_sms_app_v    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo
    ADD CONSTRAINT sms_app_vehiclemaste_vm_vehicletype_id_4bd552f3_fk_sms_app_v FOREIGN KEY (vm_vehicletype_id) REFERENCES public.sms_app_vehicletypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_vehiclemasterinfo DROP CONSTRAINT sms_app_vehiclemaste_vm_vehicletype_id_4bd552f3_fk_sms_app_v;
       public          postgres    false    315    329    3833            �           2606    44314 P   sms_app_vendor_info sms_app_vendor_info_vend_city_id_81197869_fk_sms_app_city_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vendor_info
    ADD CONSTRAINT sms_app_vendor_info_vend_city_id_81197869_fk_sms_app_city_id FOREIGN KEY (vend_city_id) REFERENCES public.sms_app_city(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.sms_app_vendor_info DROP CONSTRAINT sms_app_vendor_info_vend_city_id_81197869_fk_sms_app_city_id;
       public          postgres    false    3739    237    327            �           2606    44319 M   sms_app_vendor_info sms_app_vendor_info_vend_country_id_23d99c63_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vendor_info
    ADD CONSTRAINT sms_app_vendor_info_vend_country_id_23d99c63_fk_sms_app_c FOREIGN KEY (vend_country_id) REFERENCES public.sms_app_country(id) DEFERRABLE INITIALLY DEFERRED;
 w   ALTER TABLE ONLY public.sms_app_vendor_info DROP CONSTRAINT sms_app_vendor_info_vend_country_id_23d99c63_fk_sms_app_c;
       public          postgres    false    327    3742    239            �           2606    44324 R   sms_app_vendor_info sms_app_vendor_info_vend_state_id_15b81b8a_fk_sms_app_state_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vendor_info
    ADD CONSTRAINT sms_app_vendor_info_vend_state_id_15b81b8a_fk_sms_app_state_id FOREIGN KEY (vend_state_id) REFERENCES public.sms_app_state(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_vendor_info DROP CONSTRAINT sms_app_vendor_info_vend_state_id_15b81b8a_fk_sms_app_state_id;
       public          postgres    false    3808    327    291            �           2606    44329 L   sms_app_vendor_info sms_app_vendor_info_vend_status_id_659d6836_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_vendor_info
    ADD CONSTRAINT sms_app_vendor_info_vend_status_id_659d6836_fk_sms_app_s FOREIGN KEY (vend_status_id) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 v   ALTER TABLE ONLY public.sms_app_vendor_info DROP CONSTRAINT sms_app_vendor_info_vend_status_id_659d6836_fk_sms_app_s;
       public          postgres    false    293    3810    327            �           2606    44242 Q   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_bay_id_88ec3542_fk_sms_app_b    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_bay_id_88ec3542_fk_sms_app_b FOREIGN KEY (wh_bay_id) REFERENCES public.sms_app_bayinfo(id) DEFERRABLE INITIALLY DEFERRED;
 {   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_bay_id_88ec3542_fk_sms_app_b;
       public          postgres    false    325    3734    233            �           2606    44247 T   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_branch_id_22da1bdf_fk_sms_app_l    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_branch_id_22da1bdf_fk_sms_app_l FOREIGN KEY (wh_branch_id) REFERENCES public.sms_app_location_info(id) DEFERRABLE INITIALLY DEFERRED;
 ~   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_branch_id_22da1bdf_fk_sms_app_l;
       public          postgres    false    325    3785    269            �           2606    45252 W   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_check_in_out_32f33d72_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_check_in_out_32f33d72_fk_sms_app_c FOREIGN KEY (wh_check_in_out) REFERENCES public.sms_app_check_in_out(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_check_in_out_32f33d72_fk_sms_app_c;
       public          postgres    false    363    325    3976            �           2606    45456 R   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_damages_5ae02b46_fk_sms_app_d    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_damages_5ae02b46_fk_sms_app_d FOREIGN KEY (wh_damages) REFERENCES public.sms_app_damageinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_damages_5ae02b46_fk_sms_app_d;
       public          postgres    false    253    3764    325            �           2606    45461 \   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_dimension_deviati_ea172824_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_dimension_deviati_ea172824_fk_sms_app_g FOREIGN KEY (wh_dimension_deviation) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_dimension_deviati_ea172824_fk_sms_app_g;
       public          postgres    false    263    325    3775            �           2606    44267 \   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_goods_package_typ_7fb626b6_fk_sms_app_p    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_goods_package_typ_7fb626b6_fk_sms_app_p FOREIGN KEY (wh_goods_package_type_id) REFERENCES public.sms_app_packagetype_info(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_goods_package_typ_7fb626b6_fk_sms_app_p;
       public          postgres    false    3793    325    277            �           2606    44272 W   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_goods_status_2b2f2d3e_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_goods_status_2b2f2d3e_fk_sms_app_s FOREIGN KEY (wh_goods_status) REFERENCES public.sms_app_statuslist(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_goods_status_2b2f2d3e_fk_sms_app_s;
       public          postgres    false    3810    293    325            �           2606    45466 U   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_mismatches_3d25aae9_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_mismatches_3d25aae9_fk_sms_app_g FOREIGN KEY (wh_mismatches) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
    ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_mismatches_3d25aae9_fk_sms_app_g;
       public          postgres    false    263    325    3775            �           2606    45471 \   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_no_of_units_devia_29467fea_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_no_of_units_devia_29467fea_fk_sms_app_g FOREIGN KEY (wh_no_of_units_deviation) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_no_of_units_devia_29467fea_fk_sms_app_g;
       public          postgres    false    3775    263    325            �           2606    45476 \   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_ratification_proc_ea24e93f_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_ratification_proc_ea24e93f_fk_sms_app_g FOREIGN KEY (wh_ratification_process) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_ratification_proc_ea24e93f_fk_sms_app_g;
       public          postgres    false    3775    325    263            �           2606    45197 Y   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_stack_layer_id_daed76f2_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_stack_layer_id_daed76f2_fk_sms_app_s FOREIGN KEY (wh_stack_layer_id) REFERENCES public.sms_app_stackinginfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_stack_layer_id_daed76f2_fk_sms_app_s;
       public          postgres    false    3988    375    325            �           2606    44292 R   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_unit_id_3db59ae9_fk_sms_app_u    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_unit_id_3db59ae9_fk_sms_app_u FOREIGN KEY (wh_unit_id) REFERENCES public.sms_app_unitinfo(id) DEFERRABLE INITIALLY DEFERRED;
 |   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_unit_id_3db59ae9_fk_sms_app_u;
       public          postgres    false    303    325    3820            �           2606    45451 \   sms_app_warehouse_goods_info sms_app_warehouse_go_wh_weights_deviation_d741d34a_fk_sms_app_g    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_go_wh_weights_deviation_d741d34a_fk_sms_app_g FOREIGN KEY (wh_weights_deviation) REFERENCES public.sms_app_gstexcemptioninfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_go_wh_weights_deviation_d741d34a_fk_sms_app_g;
       public          postgres    false    325    3775    263            �           2606    44967 [   sms_app_warehouse_goods_info sms_app_warehouse_goods_info_wh_uom_6b2e57d0_fk_sms_app_uom_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info
    ADD CONSTRAINT sms_app_warehouse_goods_info_wh_uom_6b2e57d0_fk_sms_app_uom_id FOREIGN KEY (wh_uom) REFERENCES public.sms_app_uom(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_goods_info DROP CONSTRAINT sms_app_warehouse_goods_info_wh_uom_6b2e57d0_fk_sms_app_uom_id;
       public          postgres    false    3978    365    325            �           2606    44224 \   sms_app_warehouse_stock_info sms_app_warehouse_st_wh_stock_invoice_cur_36d2be16_fk_sms_app_c    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_stock_info
    ADD CONSTRAINT sms_app_warehouse_st_wh_stock_invoice_cur_36d2be16_fk_sms_app_c FOREIGN KEY (wh_stock_invoice_currency_id) REFERENCES public.sms_app_currency_type(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_stock_info DROP CONSTRAINT sms_app_warehouse_st_wh_stock_invoice_cur_36d2be16_fk_sms_app_c;
       public          postgres    false    3746    243    323            �           2606    44229 \   sms_app_warehouse_stock_info sms_app_warehouse_st_wh_stock_movement_ty_0488da2a_fk_sms_app_s    FK CONSTRAINT       ALTER TABLE ONLY public.sms_app_warehouse_stock_info
    ADD CONSTRAINT sms_app_warehouse_st_wh_stock_movement_ty_0488da2a_fk_sms_app_s FOREIGN KEY (wh_stock_movement_type_id) REFERENCES public.sms_app_stock_movement_type(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_stock_info DROP CONSTRAINT sms_app_warehouse_st_wh_stock_movement_ty_0488da2a_fk_sms_app_s;
       public          postgres    false    323    295    3812            �           2606    44234 X   sms_app_warehouse_stock_info sms_app_warehouse_st_wh_stock_type_id_6ffa2856_fk_sms_app_s    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_warehouse_stock_info
    ADD CONSTRAINT sms_app_warehouse_st_wh_stock_type_id_6ffa2856_fk_sms_app_s FOREIGN KEY (wh_stock_type_id) REFERENCES public.sms_app_stock_type(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_warehouse_stock_info DROP CONSTRAINT sms_app_warehouse_st_wh_stock_type_id_6ffa2856_fk_sms_app_s;
       public          postgres    false    323    297    3814            �           2606    44218 X   sms_app_whratemasterinfo sms_app_whratemaster_whrm_storage_type_id_ec3f552d_fk_sms_app_w    FK CONSTRAINT     �   ALTER TABLE ONLY public.sms_app_whratemasterinfo
    ADD CONSTRAINT sms_app_whratemaster_whrm_storage_type_id_ec3f552d_fk_sms_app_w FOREIGN KEY (whrm_storage_type_id) REFERENCES public.sms_app_whstoragetypeinfo(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.sms_app_whratemasterinfo DROP CONSTRAINT sms_app_whratemaster_whrm_storage_type_id_ec3f552d_fk_sms_app_w;
       public          postgres    false    321    319    3837            �      x������ � �      �      x������ � �      �   �  x�u�Q��҄�a��?l<�m��t��\fN��
UI�,��f��SW�VY.˛���[>�}��o��1��6���#��?��(9}��ρT�T�M�����Bi*�6
�\��${5�.Gv��e�/�m�����u���P���#��C	��1F�s�������`��z���~�K%�)I4�lK(I���&G�i�� ^�]oZ��ګ^;��*�?.���m�Z:��/���#�����}X�b��jYo�k@�?b\F��~�^�4�.i79�y���ŀ��zK�{�h�YFW{�ixY�zŨ��\��<�������Ǡb���zKW:	52�ҕNZ�p��2��r����1±�Aն�m�·�.4,��&���K�.��W�#�c<�Mi�YGstd���U-k��5�U�F�+4��&�RhYJ�)�$maʐP̲2[N�GH�rox���DI�i:G͑�H8*`z�~���w�)w��f���I:�,Y������Q�.g�0�d�fՔ�p�b��i������0�hBxT�ׂ4/<0� LG*������v���yt#wj\�h�T@r�͞�If���T��p_zΏ�:L���O��� @�QU��]-��-���]ly����Û�� z �!6�Q��� ��>�gA�iF�?A��Uȋ�w��[���q��6{r��L}��U�q�C�=���)q�W�sƏ�(��́������sN�q]Ѝ�P㶠��)��`%���k���r��&R�1Z��r�9F�P�ƈc�(-��̸����]�4���Z(�o9�%�|� �áĐe6�j�|��GX��A�n�Vnd˶j*�2`þj03`��jL��d�����e��P@V�QĔ5*�b��D��F +T@4��~?��2����H�Q|��_��#4�+D0�����Y�9?�O��gN�#�y�LO�5L���3wC>�Qy��=:���/(�K&c����5@��#�PA6��d����%\n�s�o��C����v(����N����J�Q&p8�Sq�*z�����S���Z��� �LP���
�%1� T���(���?�b��ќ���LiD�U��\�ZB=.�BYcy5�4
$��1�QX����g�j�GYYG`�R�Z\0ٯY�,.�L�,$��5W����6L���.L#��ܪzJ-5��,E٥�Ԗ��W3ѐ%J��������T.�FV�=@�d<.Uk�򌇦bp�B��@��T��>ˍ�K�2\�v�lВ\�v��ϒX�v8�g������1����*}���p9T�D���G@���I�dZ�O�"��tӖ���k�����q������FE�wȔ�����[��YQĆ�;�hΓ0y(Z��Mqg-�I)���D��MW;1�Y�����#MjUխ�5iK��,3t��	����A�<�I����f!i5P�¼#ete�͏p\5rk�?��1fEzm�"�aY�^Z�fW��+4�s~����28�x��%([�!�����@Qf}ǡ�:��{�z<��o�RLl�5��+����َ7��}�d� X\�հo�sA6`X���gҒ=�7��$'3*o��$��U������ۭ�+����h�.ǚ�{��Hs�Yz�(�Pc̲2ӯ�|��\�w+�@�y�E�X�<��^m�<L�:zuYx�|�h���wΡAU�����s��;hԦ7�E���Q)/�����?����=����9N����ۥ�S����6�h�/�����j��G�>��܏��S��mG�c�r[�9��7ҍ�i��v�,�Erg�BQ�ݣY�kpq��*�{�)�l�C�I���Ѻ�=���+���6�G8.�(%z�854[%z[y5,�%��n�p�O)?ѭ�(�:n�n��9n�n��*��E�DV٪���;z-y��e)��'�^v"�=fr�^g%��P��������?=�S�
v��.%9�p���|>��x�I>-�=�d��_aa3iI@IY�P�r��|T-{4e&�V���g�]��*�l�������mM���Re-鸒Xt���tX+,*��%M�`
��k??��k�����@�'�bw|�6�����;���+��o?_c0�Ki!e���������CP>Y"�v����� ���7����tg�@���?�WG��h�#�CTG��h�#��#@8��n�qR(�~rS�����=��! �*�%����j]CW=�k�o�u�A�io]ch��C�^��qHV����/���ѺFz���5e�D{�C�[��u�a�-�%3����>�u�y��QՔ�* �-C��b`'sa��Yys3�KvyL�;z�6��������@���p�G.?���C鳼av���=�a��6��ve:��b`�ɽufI��䁽Y.�c
*�����z!,D�[��QԦpj�����Z&�����%tG8�K��vA���;��\ႩZ]��)\6U�k�KJ5���}�󤻓��J#�q�Z��� ���"�֠ �yɁ@~u �!��y��ў�ޙOk\�l/ �|q��f���!�KӦbqE��>�i�R��Q�ve�F��f-ivS�d�iI�RQsj�R%���afߋ\�u�jߋr�I����d�2�^���Wa^toI'h
R�o��� �c�@ڋD �b�lD"q���6>�6���{�ve(Yx���r�G�V�Bb���pGP%�����3��,.�� �d��d�H)/�4�]��P(�Y����u�㔾��]�P_4�]���K3�ei�.�0�]6�{���k���%���M���{��j�����y�8J�~�0
n�^C?l�G(٢�_�Lf�MߧqG�(s����`�".��=2��F�_�|���1>��~&mA�_�}:��� I��������A��u��5G�o袼���q*
([� =;E����	{'��p�3�?Bf[�u��1o�0��.e�wR$-G��U(�ˬ�_+�r���x�4\�4�tHQO3���F=�Y���Z��DJq��ϫ���ɱ'�������;�ST���_}`Q�u~Nl�������&�ʁ:�R���xѴ]�Sb�x��|�M�E�Zғ������OX�*��pH���&�]7Ș��);o����H�oPk��|��/��]?`c�����5�,��J�r�"r)�d��� �����y�^�z�<D�4ģPvY�z2�Q �,�a��p�����z�?P��      �   .  x�u�_O�P��ç��;'r�����jY$eJZ�kk�(GD�&�>V�uQ�ݳ�{��0ڇ�jo�$ �V{�s��Y��[7�ћ������~������v�ݶb�4���M盢t&"^ � ������TH�6� ���$�����XIwE��9ڶ��+r�QA��Q����\iwA�HlK�M�m��R��9��}�T7�Z�j��idǧ�q{�g�>+iϯ�=��GǼ���
{R��(J\�I�^����:��mbD�3�B�J�;��T�� ��Q(zn�^MM�>�p�      �      x������ � �      �      x������ � �      �   E  x�ՖMo�H�Ϟ_a͉�2�������%�*H�r@�a�;d ���}ۓq�i����p�i�}껺�@���fCP"V�*4فsK�HT��P`�������?�f]���;�܆�oׯ�mww[v��ʯ���� W�
�pB���)�Wؔ��',��@Ź�Z�
�ml���B䨄��"΂SC�x~��ϛ�}b8@xQ(��v�O��w�D�W)%43��\��A�2s9k��`]t�l__�\.�� �*A`�>ܘ
*���"Tҩ�m9�~ЅüP���
F%,(��!TU��� m�A�$<��Q���B-0�cTſ���/�����5�P(��abM��n�S�$W�.��t$�~�,�_�N *�b�e�})�/1&��r��d#�~�tPU��#�jL���U�m��m�~���|��`{�K��BFK#�'��֑�r�P$�j�LJ���n!�H� 2�pl����� Cށ�Aw���2�R����^������2�W��¡�R�z�	�B��;�
��^o?�ho��Ώ]&AW�����O�������Mٴ����=���e�^\��LO����V~�:\Q�æ�������L?�����8��ᡙ14,AV�*a�A�8S���'����W7r?�4���9���Erb�2��ŢM��4.%��pұ7�!-)�������ʞs� ����`�8S�	��~�t�'ê'Z����2��\��V�]��y�A���q���_Θ�l�� ���&#w�Ig����E����S 2A�)Z���܅�4���$Wr.�<I�l\��$'V����E��      �   �  x�m�뒣 ���l��h�]��b����\�����I�$�+�9�Д��2�b'0�m�*ds����{e��I����h�!zp�T�,�
>m����?�+���\�BzA��g�~�+��!��P��옴�*l�����#LY���⬦ꆭ��a돥�����jp#���ᨴ}Az����H���(�o�#rəG��Djűy=Yefy5�2Y̿�ܖJ��%��xw�(&�g ��d���v��t����N�`�;�J���Z�&�Y��� ���t�M�W3
{3���V2�*�oD��Єu�y��|c�;�D�dn�l0CX�{L%��Y;�ל��%sl0��?����h>2����ܔ/6�U����p�ྡྷWO�#J�!�Q���w�Y`@����ִo�]l�M�t�&���Ꙩ��ii>_M�s���ǫ�pb�YK/rѥYO�6#(���LFo�l���Z�p���ܤ��bEO��o�'kG�����K����oPFRΖ����>_[f\�yE���œJ,Zf�s]Ր�L�D\x!�>�8�^�2���ϫ�~ G<���S!��&B��p*�����fl�@S����@t������:��ew�S�A�Ö���X���ŕ��3[��1��QD�E����}������Ǖ�쓾^i��_/Μw<N���w�J���}1��!P~�a�)����Ыh��?B�����~      �   �	  x��Z�n�8��<��C�D��Y>�p7��g��}��K�['i3:IR$�T���cs��cszBȪ=�c[wO  ~	��O�J!K���*�?��?�>���r���C�������BMO��)��~G�������"-���n��X�p��F�0�hUoƶ?T/]��6�}�!k��y��g>Y�N�/���P�u4i=�3�lN��nl�����t
��j_�Su�aG�ZE%��]FS��D?�}�vw�H��@��Q��8^1���'u��0�a��4O�t�s�	^k)R�I����s;dkG7T��Wp��>���k'�����c?�bH4��վ9��ݵh@@�	QeD�j�{V7։du�3��d�/�Ye\V��n��ǯ!9	Y-��du>����8����X�b*g���ϱ.����z<�%&�H�tj&�w�,�; &=�N{r��x�A(�B�Ӄ ��PmΧ��7C{x��M���La�P&�$GID}k^�M��G�dV]j_�-�!sB�S.��z�v��{�犔��Y���s��[�d`j���p��Xh����I̶�Q���c�CP��%�q�kJI�+2�dF��L�X����sP}�K�Kia�����A-9g����rh�o䵘c�����J��DR�Z:�R��ဉ�w`?[7�R��@pJ�h������|j��b��Uw	V�T��-�vJ�bʿsz�m��0.@m)]0�cr� ����m
%���ym(`	�?���O����B"��r%�z���V�C��S��v}�=]���u�bϋ�-��&TN�
���R�$B�4�m�6YS�e�ͦi߈@�~ypE�.�)�G�bS��\I �z�'}Tu��lL�Z�A3,.C���5=�~	zV�2ȑ-r�)N�\~fJ�]3�����34�HzV�3�
ң��	�����n�L�Ej5�����(��n�eP��RS"��:�kŉ#��� �r^a��#TsI�[2 �m$���K�Ҝno���.�/0m�Hor��(3&g�47k����
ޥFy�U��kN2i�E[j2�"�%�j�>��GH6օЎN��9��Ji\Aǉ������9
�&z���7	����py@Ҝ� ����R�(�t��9GV����⣪ݮ�p��Rln-5�(��'�a�:�P;a�x���7-#�O*�@��&�Qd��3nwh��A�S�5�)� �&ܦ潜dPj�&��J?�{��%�z�i�c}�|j����\�2�	.nިUI���v��4��:��g&df�^�)�����~-cGKk�������J��/.�m3//.�2,(����9rn*�8���Q�Ú3SA8xl7����tpU�F)k �RWu��4�7�GP,%��5���4�ow��R�h���BM��@�g
���5TC��἟1}-���"*��g8������X���ji=*gHZ����<��8Og�zZI�8�/��w!z����/-Dz�b(�F:��,R�2�3\:0�a��<V�+����[�6���d����p^iq���P;�â �9�8�t�q�����f�Y���N'=�u�w��s�"X�P�uB�V���M_'M��vwhV�����Y�A�S����3،S#5�T�=��&ZN=}�z5LuBC�\aH��25�	�sO��Vs���I9��S�Ǳ��S��~$�K�)��o`��P��!+ۄQ�Ǳu�C�UR��END�W��c�4G'&�+p��Z̾�D�]l'��ޜ���6)���a���F��h�ަZ�8Q��SެHq�9a�QX��q^"�s�!���P���7I�<���t]!T֬�.Ww�	���NZ��I�Ǐa_I}���d����*_B}�Dⴲ>e}�9�������Ȑ��I�yT�`j�iFM�A6g�ׇ��@i��WF��0���4zPםV�s�<�7���!
-�������ӤaWuŰ�ưz2��<'�Q��J��?>�9H؜�F�2׸{n�����:��O4�v�_��dj�il�.�,j�-x�S
����2��!PENϞ��ܘLoi�ށ0!�P��r���������^*�DJ�Ii"�[!�^\[<T��� ��g���P7.�n�E���E�&2�����>����a<�Z�YR�������B\�+4m���#yk7]��È��O�t7���]%ao�n]���j;�3_�/�;�)��V���7.�|X�A6�N;���Z,�Bhj8y�j�B�שR,.J�Z(�	���O�Pm(0�n����-��l�F.G)-X=���"E� ��ަ��T��5ϕ#`\�I��3,.U��\��E(W�.��Z�;�j��p��R�{�9L+_�;�I�auv��Nrq���3��e�B���<���?wY\���D��]��1�/~���/=�|A      �   \  x���I��H��u�)r߲3;�`0�d���y03��]�̪V� ���O� X�,h���y5i�^�&��ѳ���HBv���d�鷫�];��E�;߁�0P���f�IUF�TG�t��(�ďW�m�qB0���F�$.���Ȼ)%i�d�Bǎ�7�����
�����X�]73mdUSY2(����}D-<��l,�8 �S�GV�w��Zse9����Y��;N=r��}?1��ѭLm'bn�n ����q�0fKC`����� Q?�JTkV/��2h)'������Jv޹KKN&,U��za�A��� wm5���d��S��@��88Ho1��i�if�:X_��t��3�1�tj�S�/SX�n^v
X��W�M�N���Ւ9�whQ�'��e�A���fF\�|��5��DڭK0�uߛ�h�wH�ɞ2Ur�]��H�b}�.}�>ߖ�+�j�Ψ$k_W���ٖ��:����fb��-N�f�5'{/SU;�\�͜e�ݷG��Yg�D/|3�Och�ع�մ]�u{7��_EÅ�g)�Ý��*K�H�r���~�k��#e&!��vC<��&��4��+�����J��\1Ӝ��
n��9��V%��!�`>�&\W����qX����.��aƪj�ԟ�}&.�kt~2��iL^������[*b��P�Ԝ�sp���\]�B܅Bu�V?�/l�b�Nf��,(�D�%�����p$�2Ac�g�a���1���'�` -x��-��-_�U)Hn�i�r-������ƾ��|�7�H�w�{�`�r+����l���F`�8��d
Zf���Q�
�Xd�P���B���g�,���O���B�i����}1���h�� O|�ρA���1p�I�`�b(s'P�y��}d�� l�\v�l,��/�0�]����酋r#v���.��e�H"Ϩ� 9Q��ȧ�2��.���]Ʈ��r����𞦵|2oܰh�R�!�U��&�cY�F�N�����Ձ�W�V��#�7���3��?��L�5qN7I���ULi-���2.������:Ϩ�q_`VY��b�u�K ��X΋$3������R`K��}��2=|�ĳ��3�c�Q��A��A��ߒI,T��5�Q㭜��\�I�g9����u��L`�'� �a�>�˝��R[@���,@�$A�tY�U��ٳg��e�gM"��R 8�{B�m�Z��z��EΦeL�ɦ� 
OV�OM��9��bKb4 ��2�@5�k�CyY��;'��4d��dR���=�D�U�wS�h��Q�?�M�_p�zF!��E�3����"�9@lq�$����۟?��E��      P      x�3�tL.�,K�2���K�0c���� ^�      �      x������ � �      D      x������ � �      �      x������ � �      �   !   x�3��1�4�4�2��13�9}���=... J8Q      �      x������ � �      F      x�3�t�HM�����2�2�KK�b���� oi7      �   H   x�3�t�H��K��4�4�2�tJ�KO�)-*򍸌9��R2�3R�*��\&��)�E�I�)@�	W� y��      B      x������ � �      �      x�3���K�L�2�v����� -�       �   '   x�3���+��LNUpI,I�2Bp3�K�3 �1z\\\ ; X      �   )   x�3����4�2�v�47�3�2�t�4������ g)�      �   .   x�3�t�,Rp�(�/*�2s<s�N����<�ʅ*����� A�=      �   �   x�]��
�0��ߧ�	��u]w�0����Ћ�:ǜ�v�)���D%	B�@<���w��!�YA�6�'���uuE�)D,c	}(�u��KP�D>��w��}57';�o0�X&
�GW���zߢӆ#�ܑg���*q�'�~�e
�q�����C����Al0�^��9B      �      x������ � �      �      x�3��N��2����S �b���� 8��      �   Z   x�3�t*��N�SH��I-�2�t.*-�HMQ��,)�2�O-��M8��sSK2�\s�S�L9C2sJ�K�3`bf�~�90N� H��      N     x���]o�0�����"Fn��aɖ�y��ЊXl���8%[l����=4-Y�2�D-���O=٭a+�o���|�����N�D��J���	r��S�gx��P�ApG�nK�:���w>DfO�̰�e�h~�c��$��:B1Ћ�{��P2�g��v��3�u<(�	k�--m�䩣<g��H�����M�T��8�D��Yx��A��5��`�c��:n�\��5�**^�(���P8�������{��#�~ 5K9V      @   S   x�5�1
�0�99��ILO�88��/��7�����L�ڶ�nIqZ��U��R�s��P��a5��5��K��kN������K      �   O   x�3�t��K�KN�4�2�HL���K��9C���J�<��ĢԌ��b�:SNǔ��̼�⒢Ē��<�X� f�I      �   >   x�3�t�,JM.�/�2��M�KLO-�2�IM�U�IML�2�t)�,
�B}Ss���=... 5B�      T   �   x�e�M
�0���^��y3i����R7�UA��`���MJ��������k��h7N�́*_�BMˠ}lA�9�'��}��	Q3��Fbr�����^��Q$@��z!Dؚu�0���:/��S��0]��n%6Xo���G�֒��Ns��8Y q9P��5����&:      >      x������ � �      �      x������ � �      <      x������ � �      �      x������ � �      :   �  x����n�@���S콰@r�?�kzh�4R!�T@u҃�n���Z�#'�!�R$��o8"���>o~�q��.�oW�^���y�٪c_0�Z�p���q%��������'��ð���N Z�qt��s��J�$����e�ڻ�GT
sCC�Ț�؞*������qҎ� �H'Gg�>��ۇq�3j���3���];fw�ǡp�6�?�[$�:�a�y�9�".��;�%����l��{0*����؏=�cR��W+�Ga�m���q���vu	Dg�1z�����"��������YRL61;�)-��������༯{�4�����!if8x��:uUT,�6Gaz��FCCzJEYa���V�"��d��?�眩κ�lAl9������G�4�?��.      �      x�3�L-�2�������� 2       �   <   x�3�t�/*O,JQp�H,JOU�MM�H��,�U�ps���2�J-K-*NŢ � F��� ;��      8      x������ � �      �      x������ � �      6   �   x���?k�@�Y�]�'��t�Ph:d
	�@�C�.��Dvm�6����y������~�����pe������3��_/�@�\��@ǵ�_U��^,�����<��)�"��a��ɤ(��򨨥,�9\�6��C	Q�T2x� �%ﰲh�,Ƀ�Al�h��)ķ6��'s^UҘ~諿��d�sn��s�(oԍ uP�= kB �u�R��j      V   �   x�u��
� ׹�_�y�A(]�D�ZC0���}�E.����$/��-%��uU��������&)�_�Ͽ~$}CJ���6cC�Ҩ�о��,e�+	N���N�[�`c͎,'�XL?)�<�|,eJ{�;��rP      �   p   x�3�t
�UpJ�K/�)-*�430003�Dq�0�	X�GeJjQbRb
������9'B������
�3R��3A�Zp¸��eV�������ZT	S�$bU���� |�*�      4   �   x�=PQ�� ��q �.{�sl��*hcL�`V��;i�ؽr�*"6n�'&\��B)q=�<�h \��Z�$��I4��w���"��a����T������	�[	��9�_��n���%�`�;S����K<)l�9��:m�)i��+lqR�'G7S�-'�����|����
�c��0�}�$>P��],��܌wr��"��^A�      �   8   x�3��H�KQ)���I��2��M�+M��2�t�/���L+�2�t.J�K����� fr�      �      x������ � �      �      x������ � �      �   ,   x�3�tN,*��Spʯ�2���OII���8srRK�b���� ��      �       x�3�t.JM�,�2�tL)K�KN����� T�?      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      2      x������ � �      J      x�3�JMN�,KM�2���/хsc���� ���      �      x�3�tL����2�-N-����� 6��      0      x������ � �      .      x������ � �      R   !   x�3�4�2�4�2�4�2�4�2�4����� '�      �   B   x�3�I���Q�KL)�4�2��N,�K,I�N�9��R2�3R�*�\ΐԜļ��<�d� E�t          =   x�3��/�V��S(�O/J-.�2����I��tN�KN��IM�2�t��-�I-�c���� �~]            x������ � �         (   x�3���+I-�K,���K��2�t��M-.�L����� ��	�            x������ � �         ;   x�3�t�H�)-�,K�2�tIM�LN,IM�2�tN,NU�W �\&��y�Ή99\1z\\\ żO      ,      x������ � �      *      x������ � �      
   #   x�3���,Q0�4�2�0��Lc�Ȍ���� �y�      H      x�3�t��2���K�H-����� ,W<      L   �   x�u�Oo�0��ɇI� ����'� Y����1���CP4u��~?�=�������bOԻ	�b`�s���Q�L��a�v�N��"g�9h1�ѥ�hB"s�?J(I��٨.�(���*�q��od�yUC@��]O����g��yb<Zge��)�P����z!,=��x}]�.���cڵ�W�y�����?�R�`�ֿ�Hm      (   $   x�3䴴01462733� CN# 4�4����� T�[            x������ � �            x������ � �      &      x������ � �      $      x������ � �            x������ � �            x������ � �            x������ � �         )   x�3�410�2�I,ITpLN�2�42p+�2��=... ��G      "      x������ � �            x������ � �          �  x����n�@��7O�{�5�=���"�z�7HQI�����ޞ�]���ؑ*�C�������}�^|�|_!atn�̉}�މ���շ�БC�ت��D�.p�����O���寧���ʡ���h�`�a=�h2'i�:��;����,.THm����v���H
��m����ժ�����p8�@:J�F�����1u���3��D%h���M�P���A�
��B��A�+/ނ|\ݭw��������nu��6��!5���� � !xu7��� �{��8��q��/`�Xx!��\L�&�%Z��1-t�CZF�4A��h��J�EɳB+ɗ�L\�N��你pLP�!�X:�rL��=%�L($�|���~4j�n�m������J
-,�G)�Z�hpҪ��w����K�N�՘�B.����q5U�S�l�)R���0(�B<&=���&��B+�V�Y�����+Q�U=��Oݱ�RkEf=I-����nf��=�@Ͳ�*@��n��'g��?�c�Z���܀	��ɓ��?�A�^��� ��4y(Z
�7}	���(��` #��<�pm-٨1l��-ck��ֿl����B��	�����˗��ɔ|�|���,1��6o�YM\(��fK���2��N�~��AlD��h�A�2u�߁��
�
��Bd���2[�m�В��Й|��.�Kqn�����BB����b�U�$q����f����            x������ � �            x������ � �            x������ � �     